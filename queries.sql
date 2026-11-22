.mode box

-- 1
-- Find incomplete orders ordering by the oldest orders first for priority
SELECT
    order_id,
    customer_id,
    order_date,
    status
FROM Orders
WHERE status IN ('Pending', 'In Progress')
ORDER BY order_date ASC;

-- 2
-- Show all orders with its associated customer
SELECT
    o.order_id,
    c.name AS Name,
    c.email AS Email,
    c.phone AS Contact,
    o.order_date as Date,
    o.status AS Status
FROM Orders AS o
INNER JOIN users AS c
    ON o.customer_id = c.user_id
ORDER BY o.order_date ASC;

-- 3
-- Which orders that don't have an employee responsible for it yet (i.e. no employee listed with it)
SELECT
    o.order_id,
    c.name AS Name,
    o.order_date,
    o.status
FROM Orders AS o
LEFT JOIN users AS e
    ON o.employee_id = e.user_id
LEFT JOIN users AS c
    ON o.customer_id = c.user_id
WHERE e.user_id IS NULL
ORDER BY o.order_date ASC;

-- 4
-- Show the details of each order (customer, product, quantity, price and total of each item)
SELECT
    o.order_id,
    c.name AS Name,
    p.name AS Product,
    oi.quantity,
    oi.unit_price,
    oi.quantity * oi.unit_price AS total
FROM Orders AS o
INNER JOIN users AS c
    ON o.customer_id = c.user_id
INNER JOIN Order_Items AS oi
    ON o.order_id = oi.order_id
INNER JOIN Products AS p
    ON oi.product_id = p.product_id
ORDER BY o.order_id, p.name;

-- 5
-- Number of orders that still need attention (in progress or pending)
SELECT
    status,
    COUNT(*) AS num_orders
FROM Orders
WHERE status NOT IN ('Completed', 'Cancelled')
GROUP BY status;

-- 6
-- Products with at least 10 units ordered (Like which products are ordered a lot with 10 being the indicator)
SELECT
    p.product_id,
    p.name AS product,
    SUM(oi.quantity) AS total_units_ordered
FROM Products AS p
INNER JOIN Order_Items AS oi
    ON p.product_id = oi.product_id
GROUP BY
    p.product_id,
    p.name
HAVING SUM(oi.quantity) >= 10
ORDER BY total_units_ordered DESC;

-- 7
-- Find ingredients with a stock amount below producing 5 batches of every product that uses it
SELECT
    i.ingredient_id,
    i.name AS ingredient,
    i.stock_amt AS in_stock,
    i.measure_unit,
    required.required_stock,
    required.required_stock - i.stock_amt AS amt_needed
FROM Ingredients AS i
INNER JOIN (
    SELECT
        ingredient_id,
        SUM(amount * 2) AS required_stock
    FROM Recipe_Ingredients
    GROUP BY ingredient_id
) AS required
    ON i.ingredient_id = required.ingredient_id
WHERE i.stock_amt < required.required_stock
ORDER BY amt_needed DESC;

-- 8
-- Find products that haven't been ordered, including their IDs and names
SELECT product_id, name
FROM Products
EXCEPT
SELECT p.product_id, p.name
FROM Products AS p
INNER JOIN Order_Items AS oi
    ON p.product_id = oi.product_id;

-- 9
-- Details of orders placed by a specific customer
SELECT *
FROM Order_Summary
WHERE customer_id = 1
ORDER BY order_date DESC;