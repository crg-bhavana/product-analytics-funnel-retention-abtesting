-- Experiment readout for purchase conversion
WITH user_level AS (
    SELECT
        user_id,
        variant,
        MAX(CASE WHEN event_name = 'purchase' THEN 1 ELSE 0 END) AS purchased
    FROM events
    GROUP BY 1, 2
),
summary AS (
    SELECT
        variant,
        COUNT(*) AS users,
        SUM(purchased) AS purchasers,
        1.0 * SUM(purchased) / COUNT(*) AS conversion_rate
    FROM user_level
    GROUP BY 1
)
SELECT *
FROM summary;
