-- One-time migration: old campaigns (company, campaign_type, start_date, duplicate campaign_intent)
-- → campaign_name, single campaign_intent (goal), no start_date.
-- Run: psql … -d marketing_db -v ON_ERROR_STOP=1 -f campaigns_schema_migration.sql

BEGIN;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'campaigns' AND column_name = 'company'
    ) THEN
        ALTER TABLE campaigns RENAME COLUMN company TO campaign_name;
    END IF;

    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'campaigns'
          AND column_name = 'campaign_type'
    ) AND EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'campaigns'
          AND column_name = 'campaign_intent'
    ) THEN
        ALTER TABLE campaigns DROP COLUMN campaign_intent;
        ALTER TABLE campaigns RENAME COLUMN campaign_type TO campaign_intent;
    ELSIF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'campaigns'
          AND column_name = 'campaign_type'
    ) THEN
        ALTER TABLE campaigns RENAME COLUMN campaign_type TO campaign_intent;
    END IF;

    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'campaigns' AND column_name = 'start_date'
    ) THEN
        ALTER TABLE campaigns DROP COLUMN start_date;
    END IF;
END $$;

DROP INDEX IF EXISTS idx_campaigns_campaign_type;
CREATE INDEX IF NOT EXISTS idx_campaigns_campaign_intent ON campaigns(campaign_intent);

COMMIT;
