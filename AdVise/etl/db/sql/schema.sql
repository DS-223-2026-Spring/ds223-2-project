-- USERS TABLE
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    age INT,
    gender TEXT,
    location TEXT,
    interests TEXT,
    device_type TEXT
);

-- ADS TABLE
CREATE TABLE IF NOT EXISTS ads (
    ad_id TEXT PRIMARY KEY,
    ad_category TEXT,
    ad_platform TEXT,
    ad_type TEXT
);

-- INTERACTIONS TABLE (FACT TABLE)
CREATE TABLE IF NOT EXISTS interactions (
    interaction_id SERIAL PRIMARY KEY,
    user_id TEXT,
    ad_id TEXT,
    impressions INT,
    clicks INT,
    conversion INT,
    time_spent_on_ad DOUBLE PRECISION,
    day_of_week TEXT,
    engagement_score DOUBLE PRECISION,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (ad_id) REFERENCES ads(ad_id)
);

-- CAMPAIGN FEATURES TABLE
CREATE TABLE IF NOT EXISTS campaign_metrics (
    interaction_id INT PRIMARY KEY,
    CTR DOUBLE PRECISION,
    conversion_rate DOUBLE PRECISION,
    campaign_intent TEXT,
    audience_temperature TEXT,
    customer_type TEXT,
    cta_type TEXT,
    cost DOUBLE PRECISION,
    revenue DOUBLE PRECISION,
    ROI DOUBLE PRECISION,
    FOREIGN KEY (interaction_id) REFERENCES interactions(interaction_id)
);
