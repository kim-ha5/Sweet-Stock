.mode box
PRAGMA foreign_keys = ON;

BEGIN TRANSACTION;

-- Users
INSERT INTO users (name, email, phone, password, role)
VALUES
    ('Avery Thomas', 'athomas@example.com', '213-555-0101', 'pass1', 'customer'),
    ('Jordan Lee', 'jordanlee@example.com', '324-354-5744', 'pass2', 'customer'),
    ('Taylor Morgan', 'taymorgan@example.com', '252-345-7854', 'pass3', 'customer'),
    ('Skyler Smith', 'ssmith@example.com', '354-867-6549', 'pass4', 'customer'),
    ('Sam Carter', 'sam.carter@example.com', '546-582-5459', 'pass5', 'employee'),
    ('Alex Wilson', 'alex.wilson@example.com', '781-596-5298', 'pass6', 'employee'),
    ('Drew Smith', 'drew.smith@example.com', '546-324-4895', 'pass7', 'employee'),
    ('Robin Garcia', 'robin.garcia@example.com', '252-894-5459', 'pass8', 'admin');

-- Products
INSERT INTO Products (name, description, price)
VALUES
    ('Blueberry Muffin', 'Muffin with blueberries', 2.50),
    ('Cinnamon Roll', 'Soft roll with cinnamon filling and sugar glaze', 3.00),
    ('Vanilla Cupcake', 'Vanilla cupcake with buttercream frosting', 2.75),
    ('White Toast', 'Loaf of sliced white bread', 4.00),
    ('Lemon Tart', 'Lemon custard filled tart', 3.00),
    ('Baguette', 'Traditional French baguette bread ', 4.25),
    ('Chocolate Chip Cookie', 'Soft cookie with chocolate chips', 2.00);

INSERT INTO Ingredients (name, measure_unit, stock_amt, last_order_date)
VALUES
    ('Flour', 'g', 1000, '2026-10-15'),
    ('Sugar', 'g', 12000, '2026-10-15'),
    ('Butter', 'g', 8000, '2026-10-18'),
    ('Eggs', 'each', 120, '2026-10-18'),
    ('Milk', 'mL', 10000, '2026-10-19'),
    ('Yeast', 'g', 1000, '2026-09-08'),
    ('Salt', 'g', 3000, '2026-10-15'),
    ('Blueberries', 'g', 4000, '2026-10-14'),
    ('Cinnamon', 'g', 1500, '2026-10-10'),
    ('Vanilla Extract', 'ml', 1000, '2026-10-01'),
    ('Lemons', 'each', 40, '2026-10-14');


-- Orders
INSERT INTO Orders (customer_id, employee_id, order_date, status)
VALUES
    (   (SELECT user_id FROM users
         WHERE name = 'Avery Thomas' AND email = 'athomas@example.com'),
        (SELECT user_id FROM users
         WHERE name = 'Alex Wilson' AND email = 'alex.wilson@example.com'),
        '2026-10-01 09:05:00',
        'Completed'
    ),
    (   (SELECT user_id FROM users
         WHERE name = 'Jordan Lee' AND email = 'jordanlee@example.com'),
        (SELECT user_id FROM users
         WHERE name = 'Sam Carter' AND email = 'sam.carter@example.com'),
        '2026-09-30 11:20:00',
        'Completed'
    ),
    (   (SELECT user_id FROM users
         WHERE name = 'Taylor Morgan' AND email = 'taymorgan@example.com'),
        (SELECT user_id FROM users
         WHERE name = 'Drew Smith' AND email = 'drew.smith@example.com'),
        '2026-10-10 13:30:00',
        'In Progress'
    ),
    (   (SELECT user_id FROM users
         WHERE name = 'Skyler Smith' AND email = 'ssmith@example.com'),
        (SELECT user_id FROM users
         WHERE name = 'Sam Carter' AND email = 'sam.carter@example.com'),
        '2026-10-19 08:35:00',
        'Pending'
    ),
    (   (SELECT user_id FROM users
         WHERE name = 'Avery Thomas' AND email = 'athomas@example.com'),
        NULL,
        '2026-10-20 10:15:00',
        'Pending'
    );

-- Items in the orders
INSERT INTO Order_Items (order_id, product_id, quantity, unit_price)
VALUES
    (   (SELECT order_id FROM Orders WHERE order_date = '2026-10-01 09:05:00'),
        (SELECT product_id FROM Products WHERE name = 'Blueberry Muffin'),
        2,
        2.50
    ),
    (   (SELECT order_id FROM Orders WHERE order_date = '2026-10-01 09:05:00'),
        (SELECT product_id FROM Products WHERE name = 'Cinnamon Roll'),
        4,
        3.00
    ),
    (   (SELECT order_id FROM Orders WHERE order_date = '2026-09-30 11:20:00'),
        (SELECT product_id FROM Products WHERE name = 'Vanilla Cupcake'),
        6,
        2.75
    ),
    (   (SELECT order_id FROM Orders WHERE order_date = '2026-10-19 08:35:00'),
        (SELECT product_id FROM Products WHERE name = 'White Toast'),
        1,
        4.00
    ),
    (   (SELECT order_id FROM Orders WHERE order_date = '2026-10-10 13:30:00'),
        (SELECT product_id FROM Products WHERE name = 'Baguette'),
        2,
        4.25
    ),
    (   (SELECT order_id FROM Orders WHERE order_date = '2026-09-30 11:20:00'),
        (SELECT product_id FROM Products WHERE name = 'Lemon Tart'),
        2,
        3.00
    ),
    (   (SELECT order_id FROM Orders WHERE order_date = '2026-09-30 11:20:00'),
        (SELECT product_id FROM Products WHERE name = 'Blueberry Muffin'),
        3,
        2.50
    ),
    (   (SELECT order_id FROM Orders WHERE order_date = '2026-10-10 13:30:00'),
        (SELECT product_id FROM Products WHERE name = 'Cinnamon Roll'),
        2,
        3.00
    ),
    (   (SELECT order_id FROM Orders WHERE order_date = '2026-10-19 08:35:00'),
        (SELECT product_id FROM Products WHERE name = 'Vanilla Cupcake'),
        4,
        2.75
    ),
    (   (SELECT order_id FROM Orders WHERE order_date = '2026-10-01 09:05:00'),
        (SELECT product_id FROM Products WHERE name = 'Baguette'),
        3,
        4.25
    ),
    (   (SELECT order_id FROM Orders WHERE order_date = '2026-10-19 08:35:00'),
        (SELECT product_id FROM Products WHERE name = 'Lemon Tart'),
        3,
        3.0
    ),
    (   (SELECT order_id FROM Orders WHERE order_date = '2026-10-20 10:15:00'),
        (SELECT product_id FROM Products WHERE name = 'Blueberry Muffin'),
        1,
        2.50
    );

-- Recipes
INSERT INTO Recipes (product_id)
VALUES
    ((SELECT product_id FROM Products WHERE name = 'White Toast')),
    ((SELECT product_id FROM Products WHERE name = 'Blueberry Muffin')),
    ((SELECT product_id FROM Products WHERE name = 'Cinnamon Roll')),
    ((SELECT product_id FROM Products WHERE name = 'Vanilla Cupcake')),
    ((SELECT product_id FROM Products WHERE name = 'Baguette')),
    ((SELECT product_id FROM Products WHERE name = 'Lemon Tart'));

INSERT INTO Recipe_Ingredients (recipe_id, ingredient_id, amount)
VALUES
    (   (SELECT recipe_id FROM Recipes WHERE product_id =
            (SELECT product_id FROM Products WHERE name = 'White Toast')
        ),
        (SELECT ingredient_id FROM Ingredients WHERE name = 'Flour'),
        500
    ),
    (   (SELECT recipe_id FROM Recipes WHERE product_id =
            (SELECT product_id FROM Products WHERE name = 'White Toast')
        ),
        (SELECT ingredient_id FROM Ingredients WHERE name = 'Salt'),
        10
    ),
    (   (SELECT recipe_id FROM Recipes WHERE product_id =
            (SELECT product_id FROM Products WHERE name = 'White Toast')
        ),
        (SELECT ingredient_id FROM Ingredients WHERE name = 'Yeast'),
        10
    ),
    (   (SELECT recipe_id FROM Recipes WHERE product_id =
            (SELECT product_id FROM Products WHERE name = 'Blueberry Muffin')
        ),
        (SELECT ingredient_id FROM Ingredients WHERE name = 'Flour'),
        200
    ),
    (   (SELECT recipe_id FROM Recipes WHERE product_id =
            (SELECT product_id FROM Products WHERE name = 'Blueberry Muffin')
        ),
        (SELECT ingredient_id FROM Ingredients WHERE name = 'Sugar'),
        800
    ),
    (
        (SELECT recipe_id FROM Recipes WHERE product_id =
            (SELECT product_id FROM Products WHERE name = 'Blueberry Muffin')
        ),
        (SELECT ingredient_id FROM Ingredients WHERE name = 'Eggs'),
        2
    ),
    (   (SELECT recipe_id FROM Recipes WHERE product_id =
            (SELECT product_id FROM Products WHERE name = 'Blueberry Muffin')
        ),
        (SELECT ingredient_id FROM Ingredients WHERE name = 'Milk'),
        100
    ),
    (   (SELECT recipe_id FROM Recipes WHERE product_id =
            (SELECT product_id FROM Products WHERE name = 'Blueberry Muffin')),
        (SELECT ingredient_id FROM Ingredients WHERE name = 'Blueberries'),
        600
    ),
    (   (SELECT recipe_id FROM Recipes WHERE product_id =
            (SELECT product_id FROM Products WHERE name = 'Cinnamon Roll')
        ),
        (SELECT ingredient_id FROM Ingredients WHERE name = 'Flour'),
        220
    ),
    (   (SELECT recipe_id FROM Recipes WHERE product_id =
            (SELECT product_id FROM Products WHERE name = 'Cinnamon Roll')
        ),
        (SELECT ingredient_id FROM Ingredients WHERE name = 'Sugar'),
        900
    ),
    (   (SELECT recipe_id FROM Recipes WHERE product_id =
            (SELECT product_id FROM Products WHERE name = 'Cinnamon Roll')),
        (SELECT ingredient_id FROM Ingredients WHERE name = 'Butter'),
        0.07
    ),
    (   (SELECT recipe_id FROM Recipes WHERE product_id =
            (SELECT product_id FROM Products WHERE name = 'Cinnamon Roll')
        ),
        (SELECT ingredient_id FROM Ingredients WHERE name = 'Cinnamon'),
        100
    ),
    (   (SELECT recipe_id FROM Recipes WHERE product_id =
            (SELECT product_id FROM Products WHERE name = 'Vanilla Cupcake')),
        (SELECT ingredient_id FROM Ingredients WHERE name = 'Flour'),
        150
    ),
    (   (SELECT recipe_id FROM Recipes WHERE product_id =
            (SELECT product_id FROM Products WHERE name = 'Vanilla Cupcake')
        ),
        (SELECT ingredient_id FROM Ingredients WHERE name = 'Sugar'),
        100
    ),
    (   (SELECT recipe_id FROM Recipes WHERE product_id =
            (SELECT product_id FROM Products WHERE name = 'Vanilla Cupcake')
        ),
        (SELECT ingredient_id FROM Ingredients WHERE name = 'Eggs'),
        1
    ),
    (   (SELECT recipe_id FROM Recipes WHERE product_id =
            (SELECT product_id FROM Products WHERE name = 'Vanilla Cupcake')
        ),
        (SELECT ingredient_id FROM Ingredients WHERE name = 'Vanilla Extract'),
        5
    ),
    (   (SELECT recipe_id FROM Recipes WHERE product_id =
            (SELECT product_id FROM Products WHERE name = 'Baguette')),
        (SELECT ingredient_id FROM Ingredients WHERE name = 'Flour'),
        350
    ),
    (   (SELECT recipe_id FROM Recipes WHERE product_id =
            (SELECT product_id FROM Products WHERE name = 'Baguette')
        ),
        (SELECT ingredient_id FROM Ingredients WHERE name = 'Salt'),
        10
    ),
    (   (SELECT recipe_id FROM Recipes WHERE product_id =
            (SELECT product_id FROM Products WHERE name = 'Baguette')
        ),
        (SELECT ingredient_id FROM Ingredients WHERE name = 'Yeast'),
        8
    ),
    (   (SELECT recipe_id FROM Recipes WHERE product_id =
            (SELECT product_id FROM Products WHERE name = 'Lemon Tart')
        ),
        (SELECT ingredient_id FROM Ingredients WHERE name = 'Flour'),
        180
    ),
    (   (SELECT recipe_id FROM Recipes WHERE product_id =
            (SELECT product_id FROM Products WHERE name = 'Lemon Tart')
        ),
        (SELECT ingredient_id FROM Ingredients WHERE name = 'Butter'),
        90
    ),
    (   (SELECT recipe_id FROM Recipes WHERE product_id =
            (SELECT product_id FROM Products WHERE name = 'Lemon Tart')
        ),
        (SELECT ingredient_id FROM Ingredients WHERE name = 'Sugar'),
        120
    ),
    (   (SELECT recipe_id FROM Recipes WHERE product_id =
            (SELECT product_id FROM Products WHERE name = 'Lemon Tart')
        ),
        (SELECT ingredient_id FROM Ingredients WHERE name = 'Lemons'),
        3
    );

COMMIT;

-- Testing
SELECT * FROM users;
SELECT * FROM Products;
SELECT * FROM Ingredients;
SELECT * FROM Orders;
SELECT * FROM Order_Items;
SELECT * FROM Recipes;
SELECT * FROM Recipe_Ingredients;
SELECT * FROM Order_Summary;
