"""Order validation and transaction logic."""

from typing import Any
import sqlite3


def validate_order_payload(payload: Any) -> str | None:
    """Return a client-facing validation message, or None when valid."""
    if not isinstance(payload, dict):
        return "Request body must be a JSON object"

    customer = payload.get("customer")
    items = payload.get("items")
    if not isinstance(customer, dict) or not isinstance(items, list) or not items:
        return "customer and a non-empty items list are required"
    if (
        not isinstance(customer.get("name"), str)
        or not isinstance(customer.get("email"), str)
        or not customer["name"].strip()
        or not customer["email"].strip()
    ):
        return "customer.name and customer.email are required"

    for item in items:
        if not isinstance(item, dict):
            return "Each item must be an object"
        product_id = item.get("product_id")
        quantity = item.get("quantity")
        if (
            isinstance(product_id, bool)
            or isinstance(quantity, bool)
            or not isinstance(product_id, int)
            or not isinstance(quantity, int)
            or product_id <= 0
            or quantity <= 0
        ):
            return "Each item needs a positive integer product_id and quantity"
    return None


def save_order(
    database: sqlite3.Connection,
    customer_id: int,
    items: list[dict[str, Any]],
) -> int:
    """Save an order, its items, and inventory changes in one transaction."""
    with database:
        order_cursor = database.execute(
            """
            INSERT INTO Orders (customer_id, employee_id, status)
            VALUES (?, NULL, 'Pending')
            """,
            (customer_id,),
        )
        order_id = order_cursor.lastrowid

        for item in items:
            product_id = item["product_id"]
            quantity = item["quantity"]
            product = database.execute(
                "SELECT price FROM Products WHERE product_id = ?",
                (product_id,),
            ).fetchone()
            if product is None:
                raise ValueError(f"Product {product_id} was not found")

            database.execute(
                """
                INSERT INTO Order_Items (order_id, product_id, quantity, unit_price)
                VALUES (?, ?, ?, ?)
                """,
                (order_id, product_id, quantity, product["price"]),
            )

            ingredients = database.execute(
                """
                SELECT ri.ingredient_id, ri.amount * ? AS required
                FROM Recipe_Ingredients AS ri
                JOIN Recipes AS r ON r.recipe_id = ri.recipe_id
                WHERE r.product_id = ?
                """,
                (quantity, product_id),
            ).fetchall()
            for ingredient in ingredients:
                updated = database.execute(
                    """
                    UPDATE Ingredients
                    SET stock_amt = stock_amt - ?
                    WHERE ingredient_id = ? AND stock_amt >= ?
                    """,
                    (
                        ingredient["required"],
                        ingredient["ingredient_id"],
                        ingredient["required"],
                    ),
                )
                if updated.rowcount != 1:
                    raise ValueError("Insufficient ingredient stock")

    return order_id
