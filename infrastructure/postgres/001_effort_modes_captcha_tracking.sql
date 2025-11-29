-- Migration: Add effort modes, CAPTCHA tracking, and interaction logs
-- Created: 2025-11-29
-- Part of: Phase 2 Feature Completion

-- ==============================================================================
-- 1. Add effort_mode to jobs table
-- ==============================================================================

ALTER TABLE jobs ADD COLUMN IF NOT EXISTS effort_mode TEXT DEFAULT 'MEDIUM';
COMMENT ON COLUMN jobs.effort_mode IS 'LOW, MEDIUM, or HIGH - controls cost vs quality';

-- Constrain to valid values
ALTER TABLE jobs
  ADD CONSTRAINT check_effort_mode
  CHECK (effort_mode IN ('LOW', 'MEDIUM', 'HIGH'));

-- ==============================================================================
-- 2. CAPTCHA Attempts Tracking
-- ==============================================================================

CREATE TABLE IF NOT EXISTS captcha_attempts (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id          UUID REFERENCES jobs(id),
  application_id  UUID REFERENCES applications(id),
  captcha_type    TEXT NOT NULL,    -- 'recaptcha_v2', 'recaptcha_v3', 'hcaptcha', 'image'
  site_key        TEXT,              -- For reCAPTCHA/hCaptcha
  detected_at     TIMESTAMPTZ DEFAULT now(),

  -- Resolution
  solve_method    TEXT,              -- '2captcha_api', 'manual', 'failed'
  solved          BOOLEAN DEFAULT false,
  solved_at       TIMESTAMPTZ,
  solve_duration_ms INT,

  -- Cost tracking
  solve_cost_usd  NUMERIC DEFAULT 0,

  -- Error info
  error_message   TEXT,

  CONSTRAINT check_captcha_type
    CHECK (captcha_type IN ('recaptcha_v2', 'recaptcha_v3', 'hcaptcha', 'image', 'other'))
);

CREATE INDEX idx_captcha_job ON captcha_attempts(job_id);
CREATE INDEX idx_captcha_detected ON captcha_attempts(detected_at);

-- ==============================================================================
-- 3. Interaction Log (post-application tracking)
-- ==============================================================================

CREATE TABLE IF NOT EXISTS interaction_log (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id          UUID REFERENCES jobs(id),
  application_id  UUID REFERENCES applications(id),
  interaction_at  TIMESTAMPTZ DEFAULT now(),

  -- Interaction details
  channel         TEXT NOT NULL,     -- 'email', 'phone', 'platform_message', 'portal'
  direction       TEXT NOT NULL,     -- 'inbound' (from company), 'outbound' (to company)
  subject         TEXT,
  body            TEXT,

  -- Sentiment analysis
  sentiment       TEXT,              -- 'positive', 'negative', 'neutral'
  sentiment_score NUMERIC,           -- -1.0 to 1.0

  -- Classification
  message_type    TEXT,              -- 'rejection', 'interview_request', 'offer', 'question', 'other'
  requires_action BOOLEAN DEFAULT false,
  action_taken    TEXT,

  -- Metadata
  metadata        JSONB,

  CONSTRAINT check_direction
    CHECK (direction IN ('inbound', 'outbound'))
);

CREATE INDEX idx_interaction_job ON interaction_log(job_id);
CREATE INDEX idx_interaction_time ON interaction_log(interaction_at);
CREATE INDEX idx_interaction_type ON interaction_log(message_type);

-- ==============================================================================
-- 4. Effort Mode Metrics (aggregated view)
-- ==============================================================================

CREATE OR REPLACE VIEW effort_mode_stats AS
SELECT
  effort_mode,
  COUNT(*) as total_applications,
  COUNT(*) FILTER (WHERE status = 'applied') as successful,
  COUNT(*) FILTER (WHERE status = 'failed') as failed,
  AVG(cost_usd) as avg_cost,
  SUM(cost_usd) as total_cost,
  AVG(tokens_input + tokens_output) as avg_tokens,
  ROUND(
    COUNT(*) FILTER (WHERE status = 'applied')::NUMERIC /
    NULLIF(COUNT(*), 0) * 100,
    2
  ) as success_rate_pct
FROM jobs
GROUP BY effort_mode;

-- ==============================================================================
-- 5. CAPTCHA Stats (aggregated view)
-- ==============================================================================

CREATE OR REPLACE VIEW captcha_stats AS
SELECT
  captcha_type,
  COUNT(*) as total_attempts,
  COUNT(*) FILTER (WHERE solved = true) as solved_count,
  AVG(solve_duration_ms) FILTER (WHERE solved = true) as avg_solve_time_ms,
  SUM(solve_cost_usd) as total_cost,
  ROUND(
    COUNT(*) FILTER (WHERE solved = true)::NUMERIC /
    NULLIF(COUNT(*), 0) * 100,
    2
  ) as solve_rate_pct,
  solve_method
FROM captcha_attempts
GROUP BY captcha_type, solve_method;

-- ==============================================================================
-- 6. Performance Indexes
-- ==============================================================================

CREATE INDEX IF NOT EXISTS idx_jobs_effort_mode ON jobs(effort_mode);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON jobs(created_at);
CREATE INDEX IF NOT EXISTS idx_applications_job_id ON applications(job_id);

-- ==============================================================================
-- 7. Update existing rows to have default effort mode
-- ==============================================================================

UPDATE jobs SET effort_mode = 'MEDIUM' WHERE effort_mode IS NULL;

-- ==============================================================================
-- Verification
-- ==============================================================================

-- Verify tables exist
DO $$
BEGIN
  ASSERT EXISTS (SELECT FROM pg_tables WHERE tablename = 'captcha_attempts'),
    'captcha_attempts table not created';
  ASSERT EXISTS (SELECT FROM pg_tables WHERE tablename = 'interaction_log'),
    'interaction_log table not created';
  RAISE NOTICE 'Migration completed successfully ✅';
END $$;
