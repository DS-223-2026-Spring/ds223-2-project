-- =========================================
-- Fix target datatype for DS integration
-- =========================================

-- Remove old binary constraint
ALTER TABLE predictions
DROP CONSTRAINT IF EXISTS chk_target_binary;

-- Convert target column from INTEGER to VARCHAR
ALTER TABLE predictions
ALTER COLUMN target TYPE VARCHAR(50)
USING target::VARCHAR;

-- Add proper constraint for DS targets
ALTER TABLE predictions
ADD CONSTRAINT chk_target_values
CHECK (
    target IS NULL
    OR target IN (
        'ctr',
        'conversion_rate',
        'reach_score',
        'engagement_score'
    )
);