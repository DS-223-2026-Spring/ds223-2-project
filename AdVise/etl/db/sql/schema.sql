-- =============================================================
-- AdVise – Live Application Database
-- =============================================================

-- CAMPAIGNS TABLE
CREATE TABLE IF NOT EXISTS campaigns (
    campaign_id       SERIAL PRIMARY KEY,
    company           VARCHAR,
    campaign_type     VARCHAR,
    platform          VARCHAR,
    budget            FLOAT,
    duration_days     INT,
    start_date        DATE,
    campaign_intent   VARCHAR,
    product_type      VARCHAR,
    cta_type          VARCHAR,
    discount_offered  VARCHAR,
    season_month      VARCHAR,
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

-- PREDICTIONS TABLE  (one ad -> many predictions)
CREATE TABLE IF NOT EXISTS predictions (
    prediction_id              SERIAL PRIMARY KEY,
    campaign_id                INT REFERENCES campaigns(campaign_id),
    ad_id                      INT REFERENCES ads(ad_id),
    predicted_ctr              FLOAT,
    predicted_conversion_rate  FLOAT,
    predicted_engagement_score FLOAT,
    predicted_reach_score      FLOAT,
    predicted_lead_rate        FLOAT,
    predicted_metric           VARCHAR,
    predicted_value            FLOAT,
    model_version              VARCHAR,
    created_at                 TIMESTAMP DEFAULT NOW()
);

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