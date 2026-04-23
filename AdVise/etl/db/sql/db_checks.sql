-- CHECK DATA INTEGRITY
SELECT 'users' AS table_name, COUNT(*) AS n FROM users;
SELECT 'ads' AS table_name, COUNT(*) AS n FROM ads;
SELECT 'interactions' AS table_name, COUNT(*) AS n FROM interactions;
SELECT 'campaign_metrics' AS table_name, COUNT(*) AS n FROM campaign_metrics;

-- CHECK MISSING RELATIONS
SELECT
    (SELECT COUNT(*) FROM interactions i
     LEFT JOIN users u ON i.user_id = u.user_id
     WHERE u.user_id IS NULL) AS interactions_missing_user;

SELECT
    (SELECT COUNT(*) FROM interactions i
     LEFT JOIN ads a ON i.ad_id = a.ad_id
     WHERE a.ad_id IS NULL) AS interactions_missing_ad;
