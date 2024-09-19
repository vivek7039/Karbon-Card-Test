-- Query 1
SELECT u.user_id, u.username, SUM(o.total_amount) AS total_spend
FROM users u
JOIN orders o ON u.user_id = o.user_id
WHERE o.order_date >= CURRENT_DATE - 30
GROUP BY u.user_id, u.username, u.email
ORDER BY total_spend DESC
LIMIT 5;


-- Query 2
SELECT p.product_id, p.product_name, p.category, SUM(o.quantity) AS total_purchased
FROM products p
JOIN order_items o ON p.product_id = o.product_id
GROUP BY p.product_id, p.product_name, p.category
ORDER BY total_purchased DESC
LIMIT 1;