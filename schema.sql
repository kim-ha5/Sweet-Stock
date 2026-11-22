.mode box
PRAGMA foreign_keys = ON;

DROP VIEW IF EXISTS Order_Summary;
DROP TABLE IF EXISTS Recipe_Ingredients;
DROP TABLE IF EXISTS Recipes;
DROP TABLE IF EXISTS Order_Items;
DROP TABLE IF EXISTS Orders;
DROP TABLE IF EXISTS Ingredients;
DROP TABLE IF EXISTS Products;
DROP TABLE IF EXISTS users;

-- Users
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL
        CHECK (role IN ('customer', 'employee', 'admin')),
    created TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Products
CREATE TABLE Products (
    product_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    price REAL NOT NULL CHECK (price >= 0)
);

-- Orders
CREATE TABLE Orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    employee_id INTEGER,
    order_date TEXT NOT NULL DEFAULT CURRENT_DATE,
    status TEXT NOT NULL DEFAULT 'Pending'
        CHECK (
            status IN (
                'Pending',
                'In Progress',
                'Ready',
                'Completed',
                'Cancelled'
            )
        ),

    FOREIGN KEY (customer_id)
        REFERENCES users(user_id),
    FOREIGN KEY (employee_id)
        REFERENCES users(user_id)
);

CREATE TABLE Order_Items (
    item_id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price REAL NOT NULL CHECK (unit_price >= 0),

    FOREIGN KEY (order_id)
        REFERENCES Orders(order_id),
    FOREIGN KEY (product_id)
        REFERENCES Products(product_id)
);

-- Ingredients
CREATE TABLE Ingredients (
    ingredient_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    measure_unit TEXT NOT NULL,
    stock_amt REAL NOT NULL DEFAULT 0
        CHECK (stock_amt >= 0),
    last_order_date TEXT
);

-- Recipes
CREATE TABLE Recipes (
    recipe_id INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL,

    FOREIGN KEY (product_id)
        REFERENCES Products(product_id)
);

-- Recipe Ingredients
CREATE TABLE Recipe_Ingredients (
    recipe_id INTEGER NOT NULL,
    ingredient_id INTEGER NOT NULL,
    amount REAL NOT NULL CHECK (amount > 0),

    PRIMARY KEY (recipe_id, ingredient_id),

    FOREIGN KEY (recipe_id)
        REFERENCES Recipes(recipe_id),
    FOREIGN KEY (ingredient_id)
        REFERENCES Ingredients(ingredient_id)
);

-- View of all order details for summary
CREATE VIEW Order_Summary AS
SELECT
    o.order_id,
    o.customer_id,
    u.name AS customer_name,
    o.order_date,
    o.status,
    SUM(oi.quantity * oi.unit_price) AS total
FROM Orders AS o
JOIN users AS u
    ON o.customer_id = u.user_id
LEFT JOIN Order_Items AS oi
    ON o.order_id = oi.order_id
GROUP BY
    o.order_id, u.name, o.order_date, o.status;

-- Used to search for order
CREATE INDEX idx_orders
ON Orders(status, order_date)