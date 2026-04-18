-- Cohort retention analysis
WITH first_seen AS (
    SELECT
        user_id,
        MIN(DATE(event_time)) AS cohort_date
    FROM events
    GROUP BY 1
),
user_activity AS (
    SELECT DISTINCT
        e.user_id,
        f.cohort_date,
        DATE(e.event_time) AS activity_date,
        DATE(e.event_time) - f.cohort_date AS days_since_cohort
    FROM events e
    JOIN first_seen f
      ON e.user_id = f.user_id
),
cohort_sizes AS (
    SELECT
        cohort_date,
        COUNT(DISTINCT user_id) AS cohort_users
    FROM first_seen
    GROUP BY 1
)
SELECT
    a.cohort_date,
    a.days_since_cohort,
    c.cohort_users,
    COUNT(DISTINCT a.user_id) AS retained_users,
    1.0 * COUNT(DISTINCT a.user_id) / c.cohort_users AS retention_rate
FROM user_activity a
JOIN cohort_sizes c
  ON a.cohort_date = c.cohort_date
WHERE a.days_since_cohort IN (1, 7, 14, 30)
GROUP BY 1, 2, 3
ORDER BY 1, 2;
