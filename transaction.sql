PRAGMA foreign_keys = ON;

BEGIN TRANSACTION;

-- Create an order
INSERT INTO Orders (customer_id, employee_id, status)
VALUES (
    (SELECT user_id
     FROM users
     WHERE name = 'Avery Thomas'
       AND email = 'athomas@example.com'),
    NULL,
    'Pending'
);

-- Add the products for that order
INSERT INTO Order_Items (order_id, product_id, quantity, unit_price)
VALUES (
    (SELECT MAX(order_id) FROM Orders),
    (SELECT product_id FROM Products WHERE name = 'Blueberry Muffin'),
    2,
    (SELECT price FROM Products WHERE name = 'Blueberry Muffin')
);

-- Update ingredient inventory accounting for the making of the
-- added products
UPDATE Ingredients
SET stock_amt = stock_amt - (
    SELECT ri.amount * 2
    FROM Recipe_Ingredients AS ri
    INNER JOIN Recipes AS r
        ON ri.recipe_id = r.recipe_id
    WHERE r.product_id = (
        SELECT product_id
        FROM Products
        WHERE name = 'Blueberry Muffin'
    )
      AND ri.ingredient_id = Ingredients.ingredient_id
)
WHERE EXISTS (
    SELECT 1
    FROM Recipe_Ingredients AS ri
    INNER JOIN Recipes AS r
        ON ri.recipe_id = r.recipe_id
    WHERE r.product_id = (
        SELECT product_id
        FROM Products
        WHERE name = 'Blueberry Muffin'
    )
      AND ri.ingredient_id = Ingredients.ingredient_id
)
AND stock_amt >= (
    SELECT ri.amount * 2
    FROM Recipe_Ingredients AS ri
    INNER JOIN Recipes AS r
        ON ri.recipe_id = r.recipe_id
    WHERE r.product_id = (
        SELECT product_id
        FROM Products
        WHERE name = 'Blueberry Muffin'
    )
      AND ri.ingredient_id = Ingredients.ingredient_id
);

ROLLBACK;