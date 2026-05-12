-- =========================================
-- Milestone 3: Prediction schema DS update
-- =========================================

-- -------------------------
-- ADD COLUMNS (SAFE)
-- -------------------------

ALTER TABLE predictions
ADD COLUMN IF NOT EXISTS predicted_ctr_tier VARCHAR(20);

ALTER TABLE predictions
ADD COLUMN IF NOT EXISTS confidence_score DOUBLE PRECISION;

ALTER TABLE predictions
ADD COLUMN IF NOT EXISTS performance_segment VARCHAR(30);

ALTER TABLE predictions
ADD COLUMN IF NOT EXISTS target VARCHAR(50);

-- -------------------------
-- CONSTRAINTS
-- -------------------------

-- Confidence score constraint (0–1 range)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'chk_confidence_score'
    ) THEN
        ALTER TABLE predictions
        ADD CONSTRAINT chk_confidence_score
        CHECK (
            confidence_score IS NULL
            OR (confidence_score >= 0 AND confidence_score <= 1)
        );
    END IF;
END $$;

-- Target allowed values constraint
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'chk_target_values'
    ) THEN
        ALTER TABLE predictions
        ADD CONSTRAINT chk_target_values
        CHECK (
            target IS NULL OR target IN (
                'ctr',
                'conversion_rate',
                'reach_score',
                'engagement_score'
            )
        );
    END IF;
END $$;

-- -------------------------
-- INDEXES
-- -------------------------

CREATE INDEX IF NOT EXISTS idx_predictions_campaign_id
ON predictions(campaign_id);

CREATE INDEX IF NOT EXISTS idx_predictions_ad_id
ON predictions(ad_id);

CREATE INDEX IF NOT EXISTS idx_predictions_performance_segment
ON predictions(performance_segment);

CREATE INDEX IF NOT EXISTS idx_predictions_target
ON predictions(target);