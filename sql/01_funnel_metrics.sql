-- Funnel conversion by channel and device
WITH user_flags AS (
    SELECT
        user_id,
        channel,
        device,
        MAX(CASE WHEN event_name = 'visit' THEN 1 ELSE 0 END) AS visited,
        MAX(CASE WHEN event_name = 'signup' THEN 1 ELSE 0 END) AS signed_up,
        MAX(CASE WHEN event_name = 'add_to_cart' THEN 1 ELSE 0 END) AS added_to_cart,
        MAX(CASE WHEN event_name = 'purchase' THEN 1 ELSE 0 END) AS purchased
    FROM events
    GROUP BY 1, 2, 3
)
SELECT
    channel,
    device,
    SUM(visited) AS visitors,
    SUM(signed_up) AS signups,
    SUM(added_to_cart) AS add_to_carts,
    SUM(purchased) AS purchases,
    1.0 * SUM(signed_up) / NULLIF(SUM(visited), 0) AS visit_to_signup_rate,
    1.0 * SUM(added_to_cart) / NULLIF(SUM(signed_up), 0) AS signup_to_cart_rate,
    1.0 * SUM(purchased) / NULLIF(SUM(added_to_cart), 0) AS cart_to_purchase_rate,
    1.0 * SUM(purchased) / NULLIF(SUM(visited), 0) AS visit_to_purchase_rate
FROM user_flags
GROUP BY 1, 2
ORDER BY visit_to_purchase_rate DESC;
