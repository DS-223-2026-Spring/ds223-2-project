-- Row counts (MVP ERD)
SELECT 'campaigns' AS table_name, COUNT(*) AS n FROM campaigns;
SELECT 'ads' AS table_name, COUNT(*) AS n FROM ads;
SELECT 'audience' AS table_name, COUNT(*) AS n FROM audience;
SELECT 'predictions' AS table_name, COUNT(*) AS n FROM predictions;
SELECT 'training_dataset' AS table_name, COUNT(*) AS n FROM training_dataset;

-- Orphan checks (should be 0 with FKs enforced)
SELECT
    (SELECT COUNT(*) FROM ads a
     LEFT JOIN campaigns c ON a.campaign_id = c.campaign_id
     WHERE c.campaign_id IS NULL) AS ads_missing_campaign;

SELECT
    (SELECT COUNT(*) FROM predictions p
     LEFT JOIN ads a ON p.ad_id = a.ad_id
     WHERE a.ad_id IS NULL) AS predictions_missing_ad;
