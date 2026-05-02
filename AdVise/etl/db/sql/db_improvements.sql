-- =========================
-- INDEXES (Performance)
-- =========================

CREATE INDEX IF NOT EXISTS idx_ads_campaign_id ON ads(campaign_id);
CREATE INDEX IF NOT EXISTS idx_audience_campaign_id ON audience(campaign_id);
CREATE INDEX IF NOT EXISTS idx_predictions_ad_id ON predictions(ad_id);
CREATE INDEX IF NOT EXISTS idx_predictions_campaign_id ON predictions(campaign_id);

CREATE INDEX IF NOT EXISTS idx_campaigns_platform ON campaigns(platform);
CREATE INDEX IF NOT EXISTS idx_campaigns_campaign_type ON campaigns(campaign_type);

CREATE INDEX IF NOT EXISTS idx_ads_creative_type ON ads(creative_type);
CREATE INDEX IF NOT EXISTS idx_audience_location ON audience(location);

-- =========================
-- CONSTRAINTS (Data Quality)
-- =========================

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

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'ctr_range'
    ) THEN
        ALTER TABLE predictions ADD CONSTRAINT ctr_range CHECK (predicted_ctr BETWEEN 0 AND 1);
    END IF;
END$$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'conversion_range'
    ) THEN
        ALTER TABLE predictions ADD CONSTRAINT conversion_range CHECK (predicted_conversion_rate BETWEEN 0 AND 1);
    END IF;
END$$;