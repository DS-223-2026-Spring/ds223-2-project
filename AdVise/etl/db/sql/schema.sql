-- =============================================================
-- AdVise – Live Application Database
-- =============================================================

-- CAMPAIGNS TABLE
CREATE TABLE IF NOT EXISTS campaigns (
    campaign_id       SERIAL PRIMARY KEY,
    campaign_name     VARCHAR,
    campaign_intent   VARCHAR,
    platform          VARCHAR,
    budget            FLOAT,
    duration_days     INT,
    product_type      VARCHAR,
    cta_type          VARCHAR,
    created_at        TIMESTAMP DEFAULT NOW()
);

-- ADS TABLE  (one campaign -> many creatives)
CREATE TABLE IF NOT EXISTS ads (
    ad_id             SERIAL PRIMARY KEY,
    campaign_id       INT REFERENCES campaigns(campaign_id),
    creative_type     VARCHAR,
    cta_type          VARCHAR,
    copy_text_length  INT,
    aspect_ratio      VARCHAR,
    visual_complexity FLOAT,
    has_person        BOOLEAN,
    creative_url      VARCHAR,
    created_at        TIMESTAMP DEFAULT NOW()
);

-- AUDIENCE TABLE  (one campaign -> one audience record)
CREATE TABLE IF NOT EXISTS audience (
    audience_id          SERIAL PRIMARY KEY,
    campaign_id          INT REFERENCES campaigns(campaign_id),
    age                  VARCHAR,
    gender               VARCHAR,
    location             VARCHAR,
    interests            VARCHAR,
    audience_temperature VARCHAR,
    customer_type        VARCHAR,
    career               VARCHAR,
    created_at           TIMESTAMP DEFAULT NOW()
);

-- PREDICTIONS TABLE  (stored scores per ad; not the offline training_dataset)
-- predicted_tier: classifier label (low / medium / high). VARCHAR, not FLOAT, for readability.
CREATE TABLE IF NOT EXISTS predictions (
    prediction_id     SERIAL PRIMARY KEY,
    campaign_id       INT REFERENCES campaigns(campaign_id),
    ad_id              INT REFERENCES ads(ad_id),
    predicted_metric   VARCHAR,
    predicted_tier     VARCHAR(20),
    confidence         DOUBLE PRECISION,
    created_at         TIMESTAMP DEFAULT NOW()
);

-- Existing Postgres data dirs: ``CREATE TABLE IF NOT EXISTS`` never reshapes an old
-- ``predictions`` row (e.g. missing ``predicted_tier`` after a schema rename). Align
-- with ``populate_app_tables.py`` and the API preview INSERT.
ALTER TABLE predictions ADD COLUMN IF NOT EXISTS predicted_metric VARCHAR;
ALTER TABLE predictions ADD COLUMN IF NOT EXISTS predicted_tier VARCHAR(20);
ALTER TABLE predictions ADD COLUMN IF NOT EXISTS confidence DOUBLE PRECISION;

-- Drop legacy columns left on existing volumes (CREATE TABLE IF NOT EXISTS never removes them).
-- Keeps only the columns used by the API and ``populate_app_tables.py``. CASCADE drops dependent
-- indexes/views in dev; for hand-managed prod DBs, review dependencies before applying.
DO $$
DECLARE
  col text;
BEGIN
  FOR col IN
    SELECT c.column_name::text
    FROM information_schema.columns c
    WHERE c.table_schema = 'public'
      AND c.table_name = 'predictions'
      AND c.column_name NOT IN (
        'prediction_id',
        'campaign_id',
        'ad_id',
        'predicted_metric',
        'predicted_tier',
        'confidence',
        'created_at'
      )
  LOOP
    EXECUTE format('ALTER TABLE public.predictions DROP COLUMN %I CASCADE', col);
  END LOOP;
END $$;

-- At most one stored score per campaign per target metric (re-preview updates the same row).
DELETE FROM predictions p
WHERE EXISTS (
    SELECT 1
    FROM predictions p2
    WHERE p2.campaign_id = p.campaign_id
      AND p2.predicted_metric IS NOT DISTINCT FROM p.predicted_metric
      AND p2.prediction_id > p.prediction_id
);

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'uq_campaign_metric'
    ) THEN
        ALTER TABLE public.predictions
            ADD CONSTRAINT uq_campaign_metric UNIQUE (campaign_id, predicted_metric);
    END IF;
END $$;

-- =============================================================
-- INDEXES & CAMPAIGN CHECKS (kept with schema — single file)
-- =============================================================

CREATE INDEX IF NOT EXISTS idx_ads_campaign_id ON ads(campaign_id);
CREATE INDEX IF NOT EXISTS idx_audience_campaign_id ON audience(campaign_id);
CREATE INDEX IF NOT EXISTS idx_predictions_ad_id ON predictions(ad_id);
CREATE INDEX IF NOT EXISTS idx_predictions_campaign_id ON predictions(campaign_id);

CREATE INDEX IF NOT EXISTS idx_campaigns_platform ON campaigns(platform);
CREATE INDEX IF NOT EXISTS idx_campaigns_campaign_intent ON campaigns(campaign_intent);

CREATE INDEX IF NOT EXISTS idx_ads_creative_type ON ads(creative_type);
CREATE INDEX IF NOT EXISTS idx_audience_location ON audience(location);

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'budget_positive'
    ) THEN
        ALTER TABLE campaigns ADD CONSTRAINT budget_positive CHECK (budget > 0);
    END IF;
END$$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'duration_positive'
    ) THEN
        ALTER TABLE campaigns ADD CONSTRAINT duration_positive CHECK (duration_days > 0);
    END IF;
END$$;

-- =============================================================
-- OFFLINE TRAINING DATASET  (historical – for model training)
-- =============================================================
CREATE TABLE IF NOT EXISTS training_dataset (
    training_row_id      SERIAL PRIMARY KEY,
    platform             VARCHAR,
    budget               FLOAT,
    duration_days        INT,
    campaign_intent      VARCHAR,
    product_type         VARCHAR,
    cta_type             VARCHAR,
    age                  VARCHAR,
    gender               VARCHAR,
    location             VARCHAR,
    interests            VARCHAR,
    audience_temperature VARCHAR,
    customer_type        VARCHAR,
    career               VARCHAR,
    creative_type        VARCHAR,
    copy_text_length     INT,
    aspect_ratio         VARCHAR,
    visual_complexity    FLOAT,
    has_person           BOOLEAN,
    ctr                  FLOAT,
    conversion_rate      FLOAT,
    engagement_score     FLOAT,
    reach_score          FLOAT,
    lead_rate            FLOAT,
    data_source          VARCHAR,
    is_synthetic         BOOLEAN
);