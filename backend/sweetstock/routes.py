"""HTTP routes for the SweetStock API."""

import math
import sqlite3

from flask import Flask, jsonify, request

from .auth import (
    hash_password,
    password_matches,
    public_user,
    validate_login,
    validate_registration,
    clear_authenticated_user,
    set_authenticated_user,
)
from .config import VALID_STATUSES
from .database import get_database
from .orders import save_order, validate_order_payload


def register_routes(app: Flask) -> None:
    """Register all API endpoints on the application."""

    # Basic data
    @app.get("/api/health")
    def health():
        """Confirm that the API can reach the database."""
        get_database().execute("SELECT 1")
        return jsonify(status="ok")

    # Authentication
    @app.post("/api/auth/register")
    def register():
        """Create a customer or employee account."""
        payload = request.get_json(silent=True)
        validation_error = validate_registration(payload)
        if validation_error is not None:
            return jsonify(error=validation_error), 400

        database = get_database()
        email = payload["email"].strip().lower()
        try:
            cursor = database.execute(
                """
                INSERT INTO users (name, email, phone, password, role)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    payload["name"].strip(),
                    email,
                    payload["phone"].strip(),
                    hash_password(payload["password"]),
                    payload["role"],
                ),
            )
            database.commit()
        except sqlite3.IntegrityError:
            return jsonify(error="An account with that email or phone already exists"), 409

        user = database.execute(
            """
            SELECT user_id, name, email, phone, role, created
            FROM users
            WHERE user_id = ?
            """,
            (cursor.lastrowid,),
        ).fetchone()
        set_authenticated_user(user["user_id"])
        return jsonify(user=public_user(user)), 201

    @app.post("/api/auth/login")
    def login():
        """Authenticate an account and return its safe profile."""
        payload = request.get_json(silent=True)
        validation_error = validate_login(payload)
        if validation_error is not None:
            return jsonify(error=validation_error), 400

        database = get_database()
        user = database.execute(
            """
            SELECT user_id, name, email, phone, password, role, created
            FROM users
            WHERE email = ?
            """,
            (payload["email"].strip().lower(),),
        ).fetchone()
        if user is None or not password_matches(user["password"], payload["password"]):
            return jsonify(error="Incorrect email or password"), 401

        if not user["password"].startswith(("scrypt:", "pbkdf2:", "argon2:")):
            database.execute(
                "UPDATE users SET password = ? WHERE user_id = ?",
                (hash_password(payload["password"]), user["user_id"]),
            )
            database.commit()
        set_authenticated_user(user["user_id"])
        return jsonify(user=public_user(user))

    @app.post("/api/auth/logout")
    def logout():
        """End the current authenticated session."""
        clear_authenticated_user()
        return jsonify(status="ok")

    @app.get("/api/auth/me")
    def current_user():
        """Return the current authenticated user."""
        user = authenticated_user()
        if user is None:
            return jsonify(error="Authentication required"), 401
        return jsonify(user=public_user(user))

    @app.get("/api/users")
    def list_users():
        """Return all users without exposing their passwords."""
        user = authenticated_user()
        if user is None:
            return jsonify(error="Authentication required"), 401
        if user["role"] == "customer":
            return jsonify(error="Employee or admin access required"), 403
        rows = get_database().execute(
            """
            SELECT user_id, name, email, phone, role, created
            FROM users
            ORDER BY name
            """
        ).fetchall()
        return jsonify(users=[dict(row) for row in rows])

    @app.get("/api/products")
    def list_products():
        """Search or browse the bakery product catalog."""
        if authenticated_user() is None:
            return jsonify(error="Authentication required"), 401
        search = request.args.get("search", "").strip()
        rows = get_database().execute(
            """
            SELECT product_id, name, description, price
            FROM Products
            WHERE name LIKE ? OR description LIKE ?
            ORDER BY name
            """,
            (f"%{search}%", f"%{search}%"),
        ).fetchall()
        return jsonify(products=[dict(row) for row in rows])

    @app.patch("/api/products/<int:product_id>")
    def update_product(product_id: int):
        """Update a product price; only administrators may do so."""
        user = authenticated_user()
        if user is None:
            return jsonify(error="Authentication required"), 401
        if user["role"] != "admin":
            return jsonify(error="Administrator access required"), 403
        payload = request.get_json(silent=True)
        price = payload.get("price") if isinstance(payload, dict) else None
        if (
            isinstance(price, bool)
            or not isinstance(price, (int, float))
            or not math.isfinite(price)
            or price < 0
        ):
            return jsonify(error="Price must be a non-negative number"), 400
        updated = get_database().execute(
            "UPDATE Products SET price = ? WHERE product_id = ?",
            (price, product_id),
        )
        if updated.rowcount == 0:
            return jsonify(error="Product not found"), 404
        get_database().commit()
        return jsonify(product_id=product_id, price=price)

    @app.get("/api/ingredients")
    def list_ingredients():
        """Return current ingredient inventory."""
        user = authenticated_user()
        if user is None:
            return jsonify(error="Authentication required"), 401
        if user["role"] == "customer":
            return jsonify(error="Employee or admin access required"), 403
        rows = get_database().execute(
            """
            SELECT ingredient_id, name, measure_unit, stock_amt, last_order_date
            FROM Ingredients
            ORDER BY name
            """
        ).fetchall()
        return jsonify(ingredients=[dict(row) for row in rows])

    @app.get("/api/recipes")
    def list_recipes():
        """Return recipes and their ingredients for staff users."""
        user = authenticated_user()
        if user is None:
            return jsonify(error="Authentication required"), 401
        if user["role"] == "customer":
            return jsonify(error="Employee or admin access required"), 403
        rows = get_database().execute(
            """
            SELECT r.recipe_id, r.product_id, p.name AS product_name,
                   i.ingredient_id, i.name AS ingredient_name,
                   ri.amount, i.measure_unit
            FROM Recipes AS r
            JOIN Products AS p ON p.product_id = r.product_id
            JOIN Recipe_Ingredients AS ri ON ri.recipe_id = r.recipe_id
            JOIN Ingredients AS i ON i.ingredient_id = ri.ingredient_id
            ORDER BY p.name, i.name
            """
        ).fetchall()
        recipes = {}
        for row in rows:
            recipe = recipes.setdefault(
                row["recipe_id"],
                {
                    "recipe_id": row["recipe_id"],
                    "product_id": row["product_id"],
                    "product_name": row["product_name"],
                    "ingredients": [],
                },
            )
            recipe["ingredients"].append(
                {
                    "ingredient_id": row["ingredient_id"],
                    "name": row["ingredient_name"],
                    "amount": row["amount"],
                    "measure_unit": row["measure_unit"],
                }
            )
        return jsonify(recipes=list(recipes.values()))

    # Orders
    @app.get("/api/orders")
    def list_orders():
        """Search orders, optionally filtered by status."""
        user = authenticated_user()
        if user is None:
            return jsonify(error="Authentication required"), 401

        status = request.args.get("status")
        search = request.args.get("search", "").strip()
        query = """
            SELECT
                o.order_id,
                o.customer_id,
                customer.name AS customer_name,
                customer.email AS customer_email,
                o.employee_id,
                employee.name AS employee_name,
                employee.email AS employee_email,
                o.order_date,
                o.status,
                COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS total
            FROM Orders AS o
            JOIN users AS customer ON customer.user_id = o.customer_id
            LEFT JOIN users AS employee ON employee.user_id = o.employee_id
            LEFT JOIN Order_Items AS oi ON oi.order_id = o.order_id
        """
        parameters: list[str] = []
        filters = []
        if status:
            if status not in VALID_STATUSES:
                return jsonify(error="Invalid order status"), 400
            filters.append("o.status = ?")
            parameters.append(status)
        if search:
            filters.append("(customer.name LIKE ? OR CAST(o.order_id AS TEXT) LIKE ?)")
            parameters.extend((f"%{search}%", f"%{search}%"))
        if user["role"] == "customer":
            filters.append("o.customer_id = ?")
            parameters.append(user["user_id"])
        if filters:
            query += " WHERE " + " AND ".join(filters)
        query += """
            GROUP BY o.order_id
            ORDER BY o.order_date ASC, o.order_id ASC
        """
        rows = get_database().execute(query, parameters).fetchall()
        return jsonify(orders=[dict(row) for row in rows])

    @app.get("/api/orders/<int:order_id>")
    def get_order(order_id: int):
        """Return one order with its line items and total."""
        user = authenticated_user()
        if user is None:
            return jsonify(error="Authentication required"), 401
        database = get_database()
        order = database.execute(
            """
            SELECT
                o.order_id, o.order_date, o.status,
                customer.user_id AS customer_id,
                customer.name AS customer_name,
                customer.email AS customer_email,
                employee.user_id AS employee_id,
                employee.name AS employee_name,
                employee.email AS employee_email
            FROM Orders AS o
            JOIN users AS customer ON customer.user_id = o.customer_id
            LEFT JOIN users AS employee ON employee.user_id = o.employee_id
            WHERE o.order_id = ?
            """,
            (order_id,),
        ).fetchone()
        if order is None:
            return jsonify(error="Order not found"), 404
        if user["role"] == "customer" and order["customer_id"] != user["user_id"]:
            return jsonify(error="Order not found"), 404

        items = database.execute(
            """
            SELECT oi.item_id, oi.product_id, p.name, oi.quantity, oi.unit_price,
                   oi.quantity * oi.unit_price AS total
            FROM Order_Items AS oi
            JOIN Products AS p ON p.product_id = oi.product_id
            WHERE oi.order_id = ?
            ORDER BY oi.item_id
            """,
            (order_id,),
        ).fetchall()
        total = database.execute(
            "SELECT COALESCE(SUM(quantity * unit_price), 0) AS total FROM Order_Items WHERE order_id = ?",
            (order_id,),
        ).fetchone()["total"]
        result = dict(order)
        result["items"] = [dict(item) for item in items]
        result["total"] = total
        return jsonify(order=result)

    @app.post("/api/orders")
    def create_order():
        """Create an order and deduct recipe ingredients atomically."""
        payload = request.get_json(silent=True)
        validation_error = validate_order_payload(payload)
        if validation_error is not None:
            return jsonify(error=validation_error), 400

        user = authenticated_user()
        if user is None:
            return jsonify(error="Authentication required"), 401
        database = get_database()
        customer = payload["customer"]
        if user["role"] == "customer" and (
            customer["email"].strip().lower() != user["email"]
            or customer["name"].strip() != user["name"]
        ):
            return jsonify(error="Customers can only create orders for themselves"), 403
        customer_row = database.execute(
            """
            SELECT user_id
            FROM users
            WHERE name = ? AND email = ? AND role = 'customer'
            """,
            (customer["name"], customer["email"]),
        ).fetchone()
        if customer_row is None:
            return jsonify(error="Customer was not found"), 404

        try:
            order_id = save_order(database, customer_row["user_id"], payload["items"])
        except ValueError as error:
            return jsonify(error=str(error)), 400

        return jsonify(order_id=order_id, status="Pending"), 201

    @app.patch("/api/orders/<int:order_id>")
    def update_order(order_id: int):
        """Change an order's workflow status."""
        user = authenticated_user()
        if user is None:
            return jsonify(error="Authentication required"), 401
        if user["role"] == "customer":
            return jsonify(error="Employee or admin access required"), 403
        payload = request.get_json(silent=True)
        status = payload.get("status") if isinstance(payload, dict) else None
        if status not in VALID_STATUSES:
            return jsonify(error="Choose a valid order status"), 400

        updated = get_database().execute(
            "UPDATE Orders SET status = ? WHERE order_id = ?",
            (status, order_id),
        )
        if updated.rowcount == 0:
            return jsonify(error="Order not found"), 404
        get_database().commit()
        return jsonify(order_id=order_id, status=status)

    @app.patch("/api/ingredients/<int:ingredient_id>/stock")
    def restock_ingredient(ingredient_id: int):
        """Add a positive amount to ingredient inventory."""
        user = authenticated_user()
        if user is None:
            return jsonify(error="Authentication required"), 401
        if user["role"] == "customer":
            return jsonify(error="Employee or admin access required"), 403
        payload = request.get_json(silent=True)
        amount = payload.get("amount") if isinstance(payload, dict) else None
        if (
            isinstance(amount, bool)
            or not isinstance(amount, (int, float))
            or not math.isfinite(amount)
            or amount <= 0
        ):
            return jsonify(error="Restock amount must be a positive number"), 400

        updated = get_database().execute(
            """
            UPDATE Ingredients
            SET stock_amt = stock_amt + ?, last_order_date = CURRENT_DATE
            WHERE ingredient_id = ?
            """,
            (amount, ingredient_id),
        )
        if updated.rowcount == 0:
            return jsonify(error="Ingredient not found"), 404
        get_database().commit()
        return jsonify(ingredient_id=ingredient_id, added=amount)

    # Reports
    @app.get("/api/reports/incomplete-orders")
    def incomplete_orders():
        """Return pending and in-progress orders."""
        user = authenticated_user()
        if user is None:
            return jsonify(error="Authentication required"), 401
        customer_filter = ""
        parameters: tuple[int, ...] = ()
        if user["role"] == "customer":
            customer_filter = "AND customer_id = ?"
            parameters = (user["user_id"],)
        rows = get_database().execute(
            f"""
            SELECT order_id, customer_id, order_date, status
            FROM Orders
            WHERE status IN ('Pending', 'In Progress')
            {customer_filter}
            ORDER BY order_date ASC
            """,
            parameters,
        ).fetchall()
        return jsonify(orders=[dict(row) for row in rows])

    @app.get("/api/reports/unassigned-orders")
    def unassigned_orders():
        """Return orders that do not have an employee assigned."""
        user = authenticated_user()
        if user is None:
            return jsonify(error="Authentication required"), 401
        if user["role"] == "customer":
            return jsonify(error="Employee or admin access required"), 403
        rows = get_database().execute(
            """
            SELECT o.order_id, c.name, c.email, o.order_date, o.status
            FROM Orders AS o
            JOIN users AS c ON c.user_id = o.customer_id
            LEFT JOIN users AS e ON e.user_id = o.employee_id
            WHERE e.user_id IS NULL
            ORDER BY o.order_date ASC
            """
        ).fetchall()
        return jsonify(orders=[dict(row) for row in rows])

    @app.get("/api/reports/unordered-products")
    def unordered_products():
        """Return products that have never been included in an order."""
        user = authenticated_user()
        if user is None:
            return jsonify(error="Authentication required"), 401
        if user["role"] == "customer":
            return jsonify(error="Employee or admin access required"), 403
        rows = get_database().execute(
            """
            SELECT p.product_id, p.name
            FROM Products AS p
            WHERE NOT EXISTS (
                SELECT 1
                FROM Order_Items AS oi
                WHERE oi.product_id = p.product_id
            )
            ORDER BY p.product_id
            """
        ).fetchall()
        return jsonify(products=[dict(row) for row in rows])

    @app.get("/api/reports/low-stock")
    def low_stock():
        """Return ingredients below the two-batch threshold."""
        user = authenticated_user()
        if user is None:
            return jsonify(error="Authentication required"), 401
        if user["role"] == "customer":
            return jsonify(error="Employee or admin access required"), 403
        rows = get_database().execute(
            """
            SELECT i.ingredient_id, i.name, i.stock_amt, i.measure_unit,
                   required.required_stock,
                   required.required_stock - i.stock_amt AS amount_needed
            FROM Ingredients AS i
            JOIN (
                SELECT ingredient_id, SUM(amount * 2) AS required_stock
                FROM Recipe_Ingredients
                GROUP BY ingredient_id
            ) AS required ON required.ingredient_id = i.ingredient_id
            WHERE i.stock_amt < required.required_stock
            ORDER BY amount_needed DESC
            """
        ).fetchall()
        return jsonify(ingredients=[dict(row) for row in rows])

    @app.get("/api/reports/sales-summary")
    def sales_summary():
        """Summarize order counts and sales by status using related tables."""
        user = authenticated_user()
        if user is None:
            return jsonify(error="Authentication required"), 401
        if user["role"] == "customer":
            return jsonify(error="Employee or admin access required"), 403
        rows = get_database().execute(
            """
            SELECT o.status,
                   COUNT(DISTINCT o.order_id) AS order_count,
                   COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS sales_total
            FROM Orders AS o
            JOIN users AS customer ON customer.user_id = o.customer_id
            LEFT JOIN Order_Items AS oi ON oi.order_id = o.order_id
            GROUP BY o.status
            ORDER BY sales_total DESC
            """
        ).fetchall()
        totals = get_database().execute(
            """
            SELECT COUNT(DISTINCT o.order_id) AS order_count,
                   COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS sales_total,
                   COUNT(DISTINCT CASE WHEN o.status IN ('Pending', 'In Progress') THEN o.order_id END) AS open_orders,
                   COUNT(DISTINCT CASE WHEN o.status = 'Completed' THEN o.order_id END) AS completed_orders,
                   (SELECT COUNT(*) FROM Ingredients) AS inventory_count
            FROM Orders AS o
            LEFT JOIN Order_Items AS oi ON oi.order_id = o.order_id
            """
        ).fetchone()
        return jsonify(summary={"rows": [dict(row) for row in rows], "totals": dict(totals)})

    @app.get("/api/reports/customer-summary")
    def customer_summary():
        """Return aggregate order history for the authenticated customer."""
        user = authenticated_user()
        if user is None:
            return jsonify(error="Authentication required"), 401
        if user["role"] != "customer":
            return jsonify(error="Customer access required"), 403
        summary = get_database().execute(
            """
            SELECT COUNT(DISTINCT o.order_id) AS order_count,
                   COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS sales_total
            FROM Orders AS o
            LEFT JOIN Order_Items AS oi ON oi.order_id = o.order_id
            WHERE o.customer_id = ?
            """,
            (user["user_id"],),
        ).fetchone()
        return jsonify(summary=dict(summary))


def authenticated_user():
    """Load the signed-in user from the Flask session."""
    from flask import session

    user_id = session.get("user_id")
    if user_id is None:
        return None
    return get_database().execute(
        """
        SELECT user_id, name, email, phone, role, created
        FROM users
        WHERE user_id = ?
        """,
        (user_id,),
    ).fetchone()
