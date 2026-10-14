# Tokenized Billing System Database Schema
# PostgreSQL migration scripts for token-based billing
# Supports multi-modal AI (text, image, video, agent orchestration)
# Implements tier-based quotas and usage tracking
# 
# Migration from SQLite to PostgreSQL
# Version: 1.0.0
# Date: 2026-01-15

-- ============================================================================
-- TABLE 1: TOKEN_ACCOUNTS
-- Manages user token balances and tiers
-- ============================================================================

CREATE TABLE IF NOT EXISTS token_accounts (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL UNIQUE,
    balance DECIMAL(15, 4) DEFAULT 0.0000,
    currency VARCHAR(3) DEFAULT 'USD',
    tier VARCHAR(20) NOT NULL CHECK (tier IN ('Free', 'SME', 'Business', 'Enterprise')),
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'cancelled')),
    rollover_balance DECIMAL(15, 4) DEFAULT 0.0000,
    last_token_charge_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for token accounts
CREATE INDEX idx_token_user ON token_accounts(user_id, tier);
CREATE INDEX idx_token_balance ON token_accounts(balance);
CREATE INDEX idx_token_status ON token_accounts(status);

-- ============================================================================
-- TABLE 2: TOKEN_TRANSACTIONS
-- Detailed transaction log for all token movements
-- ============================================================================

CREATE TABLE IF NOT EXISTS token_transactions (
    id VARCHAR(36) PRIMARY KEY,
    token_account_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    
    -- Transaction Details
    transaction_type VARCHAR(50) NOT NULL CHECK (transaction_type IN ('purchase', 'usage', 'refund', 'bonus', 'rollover', 'adjustment')),
    amount DECIMAL(15, 4) NOT NULL,
    balance_after DECIMAL(15, 4) NOT NULL,
    
    -- Service Details
    service_type VARCHAR(50) NOT NULL CHECK (service_type IN ('text_llm', 'image_generation', 'video_generation', 'agent_orchestration', 'analysis', 'transcription')),
    model_id VARCHAR(100),
    provider_id VARCHAR(50) NOT NULL,
    modality VARCHAR(20) NOT NULL CHECK (modality IN ('text', 'image', 'video', 'multi_modal')),
    operation_id VARCHAR(100),
    operation_type VARCHAR(50),
    
    -- Usage Metrics
    input_tokens INTEGER,
    output_tokens INTEGER,
    tokens_consumed INTEGER NOT NULL,
    estimated_cost_usd DECIMAL(10, 4),
    
    -- Metadata
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_token_account FOREIGN KEY (token_account_id) REFERENCES token_accounts(id) ON DELETE CASCADE
);

-- Indexes for token transactions
CREATE INDEX idx_transaction_user_date ON token_transactions(user_id, created_at);
CREATE INDEX idx_transaction_type ON token_transactions(transaction_type, service_type);
CREATE INDEX idx_transaction_operation ON token_transactions(operation_id);

-- ============================================================================
-- TABLE 3: TOKEN_PACKAGES
-- Predefined token packages users can purchase
-- ============================================================================

CREATE TABLE IF NOT EXISTS token_packages (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10, 4) NOT NULL,
    token_amount DECIMAL(12, 0) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    tier VARCHAR(20) CHECK (tier IN ('Free', 'SME', 'Business', 'Enterprise')),
    bonus_tokens INTEGER DEFAULT 0,
    features JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for token packages
CREATE INDEX idx_package_tier ON token_packages(tier, is_active);

-- Default token packages
INSERT INTO token_packages (id, name, description, price, token_amount, tier, features, is_active) VALUES
-- Free Tier Packages
('pkg-free-0', 'Free Tier - Monthly Allowance', '0 tokens per month - includes basic features', 0.00, 0, 'Free', 
 '{"features": ["bmc", "leads", "copywriter", "visual", "video"], "requests_per_day": 50, "images_per_day": 10, "videos_per_month": 0}'::JSONB, true),
-- SME Tier Packages
('pkg-sme-monthly', 'SME Monthly Plan', '$19/month for 10,000 tokens - includes all free features + strategy advisor + analytics', 19.00, 10000, 'SME',
 '{"features": ["all_free", "strategy_advisor", "analytics", "api_access"], "requests_per_day": 500, "images_per_day": 50, "videos_per_month": 5, "rollover": true}'::JSONB, true),
('pkg-sme-quarterly', 'SME Quarterly Plan', '$50/quarter for 30,000 tokens (2.5% savings)', 50.00, 30000, 'SME',
'{"features": ["all_free", "strategy_advisor", "analytics", "api_access"], "requests_per_day": 500, "images_per_day": 50, "videos_per_month": 5, "rollover": true, "discount": "2.5"}'::JSONB, true),
-- Business Tier Packages
('pkg-business-monthly', 'Business Monthly Plan', '$49/month for 40,000 tokens - includes all SME features + priority support', 49.00, 40000, 'Business',
'{"features": ["all_sme", "priority_support", "white_label", "api_access"], "requests_per_day": 2000, "images_per_day": 200, "videos_per_month": 20, "rollover": true, "priority_support": true}'::JSONB, true),
('pkg-business-quarterly', 'Business Quarterly Plan', '$140/quarter for 120,000 tokens (5% savings)', 140.00, 120000, 'Business',
'{"features": ["all_sme", "priority_support", "white_label", "api_access"], "requests_per_day": 2000, "images_per_day": 200, "videos_per_month": 20, "rollover": true, "discount": "5.0"}'::JSONB, true),
-- Enterprise Tier
('pkg-enterprise', 'Enterprise Custom Plan', 'Custom pricing based on usage - includes all features + dedicated support + SLA', NULL, NULL, 'Enterprise',
'{"features": ["all_business", "dedicated_support", "sla", "custom_integration", "api_access"], "requests_per_day": 10000, "images_per_day": 1000, "videos_per_month": 100, "rollover": true, "priority_support": true, "sla": true}'::JSONB, true);

-- ============================================================================
-- TABLE 4: USAGE_QUOTAS
-- Usage limits per tier
-- ============================================================================

CREATE TABLE IF NOT EXISTS usage_quotas (
    id VARCHAR(36) PRIMARY KEY,
    token_account_id VARCHAR(36) NOT NULL,
    tier VARCHAR(20) NOT NULL,
    period_type VARCHAR(20) NOT NULL CHECK (period_type IN ('daily', 'monthly', 'annual')),
    
    -- Quota Limits
    max_tokens INTEGER NOT NULL,
    max_images INTEGER DEFAULT 0,
    max_videos INTEGER DEFAULT 0,
    max_agents INTEGER DEFAULT 0,
    max_api_calls INTEGER DEFAULT 0,
    
    -- Usage Tracking
    tokens_used INTEGER DEFAULT 0,
    images_used INTEGER DEFAULT 0,
    videos_used INTEGER DEFAULT 0,
    agents_used INTEGER DEFAULT 0,
    api_calls_used INTEGER DEFAULT 0,
    
    -- Reset Schedule
    reset_day INTEGER, -- Day of month for reset (1-31)
    last_reset TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_quota_account FOREIGN KEY (token_account_id) REFERENCES token_accounts(id) ON DELETE CASCADE,
    UNIQUE (token_account_id, tier, period_type)
);

-- Index for quotas
CREATE INDEX idx_quota_account_tier ON usage_quotas(token_account_id, tier, period_type);

-- Default quotas per tier
INSERT INTO usage_quotas (id, token_account_id, tier, period_type, max_tokens, max_images, max_videos, max_agents, max_api_calls) VALUES
-- Free Tier
('quota-free-monthly', 'user-free', 'Free', 'monthly', 0, 10, 0, 0, 50),
('quota-free-daily', 'user-free', 'Free', 'daily', 0, 10, 0, 0, 50),
-- SME Tier
('quota-sme-monthly', 'user-sme', 'SME', 'monthly', 10000, 50, 5, 10, 500),
('quota-sme-daily', 'user-sme', 'SME', 'daily', 350, 50, 5, 10, 500),
-- Business Tier
('quota-business-monthly', 'user-business', 'Business', 'monthly', 40000, 200, 20, 20, 2000),
('quota-business-daily', 'user-business', 'Business', 'daily', 1400, 200, 20, 20, 2000),
-- Enterprise Tier
('quota-enterprise-monthly', 'user-enterprise', 'Enterprise', 'monthly', NULL, 1000, 100, 100, 10000),
('quota-enterprise-daily', 'user-enterprise', 'Enterprise', 'daily', NULL, 1000, 100, 100, 10000);

-- ============================================================================
-- TABLE 5: PROVIDER_COST_RATES
-- Tracks costs per AI provider and model
-- ============================================================================

CREATE TABLE IF NOT EXISTS provider_cost_rates (
    id VARCHAR(36) PRIMARY KEY,
    provider_id VARCHAR(50) NOT NULL UNIQUE,
    provider_name VARCHAR(100) NOT NULL,
    service_type VARCHAR(50) NOT NULL CHECK (service_type IN ('text_llm', 'image_generation', 'video_generation', 'agent_orchestration', 'analysis', 'transcription')),
    model_id VARCHAR(100),
    
    -- Cost Configuration
    price_per_1k_tokens DECIMAL(10, 6) NOT NULL,
    price_per_image DECIMAL(10, 4),
    price_per_video_second DECIMAL(10, 4),
    price_per_agent_call DECIMAL(10, 4),
    currency VARCHAR(3) DEFAULT 'USD',
    
    -- Negotiated Rates
    is_negotiated BOOLEAN DEFAULT false,
    volume_discount_percent DECIMAL(5, 2) DEFAULT 0.00,
    
    -- Performance
    avg_latency_ms INTEGER,
    success_rate DECIMAL(5, 2),
    last_updated TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for provider costs
CREATE INDEX idx_provider_service ON provider_cost_rates(provider_id, service_type);

-- Default provider cost rates
INSERT INTO provider_cost_rates (id, provider_id, provider_name, service_type, price_per_1k_tokens, price_per_image, price_per_video_second, price_per_agent_call, currency, avg_latency_ms, success_rate) VALUES
-- Text LLM Providers
('cost-gpt4-turbo', 'groq', 'Groq GPT-4 Turbo', 'text_llm', 'gpt-4-turbo', 0.010, NULL, NULL, NULL, 'USD', 200, 98.5),
('cost-gpt4', 'openai', 'GPT-4', 'text_llm', 'gpt-4', 0.030, NULL, NULL, NULL, 'USD', 400, 97.2),
('cost-gemini-1.5-pro', 'google', 'Gemini 1.5 Pro', 'text_llm', 'gemini-1.5-pro', 0.035, NULL, NULL, NULL, 'USD', 500, 99.0),
('cost-claude-3-opus', 'anthropic', 'Claude 3 Opus', 'text_llm', 'claude-3-opus', 0.015, NULL, NULL, NULL, 'USD', 300, 99.5),
-- Image Generation Providers
('cost-flux-1-dev', 'replicate', 'FLUX.1-dev', 'image_generation', 'flux-1-dev', 0.0025, NULL, NULL, NULL, 'USD', 2000, 99.0),
('cost-dalle-3', 'openai', 'DALL-E 3', 'image_generation', 'dall-e-3', 0.040, NULL, NULL, NULL, 'USD', 5000, 99.0),
('cost-sdxl', 'replicate', 'SDXL', 'image_generation', 'sdxl', 0.0030, NULL, NULL, NULL, 'USD', 3000, 99.0),
-- Video Generation Providers
('cost-veo-3', 'google', 'Veo 3', 'video_generation', 'veo-3', NULL, 0.05, NULL, 'USD', 8000, 99.0),
('cost-kling-ai', 'kling', 'Kling AI', 'video_generation', 'kling-ai', NULL, 0.02, NULL, NULL, 'USD', 5000, 98.0),
('cost-luma', 'runway', 'Luma', 'video_generation', 'luma-dream-machine', NULL, 0.03, NULL, NULL, 'USD', 4000, 97.0);
-- Agent Orchestration Providers
('cost-langchain', 'anthropic', 'LangChain', 'agent_orchestration', 'langchain', NULL, NULL, 0.050, 'USD', 500, 99.5),
('cost-langgraph', 'langchain', 'LangGraph', 'agent_orchestration', 'langgraph', NULL, NULL, 0.050, 'USD', 500, 99.5),
-- Analysis Providers
('cost-openai-analysis', 'openai', 'OpenAI Analysis', 'analysis', 'gpt-4-vision', NULL, NULL, 0.010, NULL, 'USD', 1500, 99.0);

-- ============================================================================
-- TABLE 6: MODEL_PREFERENCES
-- Stores user's preferred models for each service type
-- ============================================================================

CREATE TABLE IF NOT EXISTS model_preferences (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL UNIQUE,
    
    -- Preferred Models
    preferred_text_llm_model VARCHAR(100),
    preferred_text_llm_provider VARCHAR(50),
    preferred_image_generation_model VARCHAR(100),
    preferred_image_generation_provider VARCHAR(50),
    preferred_video_generation_model VARCHAR(100),
    preferred_video_generation_provider VARCHAR(50),
    preferred_agent_orchestration_provider VARCHAR(50),
    
    -- Settings
    smart_selection_enabled BOOLEAN DEFAULT true,
    auto_select_cheapest BOOLEAN DEFAULT true,
    max_cost_per_operation DECIMAL(10, 4),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for model preferences
CREATE INDEX idx_model_preferences_user ON model_preferences(user_id);

-- ============================================================================
-- TABLE 7: TOKEN_USAGE_ALERTS
-- Tracks when users approach quota limits
-- ============================================================================

CREATE TABLE IF NOT EXISTS token_usage_alerts (
    id VARCHAR(36) PRIMARY KEY,
    token_account_id VARCHAR(36) NOT NULL,
    
    -- Alert Details
    alert_type VARCHAR(50) NOT NULL CHECK (alert_type IN ('quota_warning', 'quota_exceeded', 'cost_surge', 'usage_anomaly')),
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('info', 'warning', 'critical', 'emergency')),
    service_type VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    
    -- Metrics
    current_tokens_remaining INTEGER NOT NULL,
    percentage_used DECIMAL(5, 2) NOT NULL,
    estimated_time_remaining INTERVAL,
    
    -- Resolution
    is_resolved BOOLEAN DEFAULT false,
    resolved_at TIMESTAMP,
    
    -- Metadata
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_alert_account FOREIGN KEY (token_account_id) REFERENCES token_accounts(id) ON DELETE CASCADE
);

-- Index for alerts
CREATE INDEX idx_alert_account_type ON token_usage_alerts(token_account_id, alert_type);
CREATE INDEX idx_alert_severity ON token_usage_alerts(severity);

-- ============================================================================
-- FUNCTIONS AND TRIGGERS
-- ============================================================================

-- Function to update quota usage
CREATE OR REPLACE FUNCTION update_quota_usage(
    p_token_account_id VARCHAR,
    p_service_type VARCHAR,
    p_tier VARCHAR,
    p_period_type VARCHAR,
    p_amount INTEGER
) RETURNS VOID AS $$
BEGIN
    UPDATE usage_quotas
    SET tokens_used = tokens_used + p_amount
    WHERE token_account_id = p_token_account_id
      AND tier = p_tier
      AND period_type = p_period_type;
END;
$$ LANGUAGE plpgsql;

-- Function to check quota before operation
CREATE OR REPLACE FUNCTION check_quota_limits(
    p_user_id VARCHAR,
    p_service_type VARCHAR,
    p_tier VARCHAR,
    p_required_tokens INTEGER
) RETURNS JSON AS $$
DECLARE
    v_tokens_used INTEGER;
    v_max_tokens INTEGER;
    v_remaining INTEGER;
BEGIN
    -- Get current usage
    SELECT uq.tokens_used, uq.max_tokens
    INTO v_tokens_used, v_max_tokens
    FROM usage_quotas uq
    JOIN token_accounts ta ON uq.token_account_id = ta.id
    WHERE ta.user_id = p_user_id
      AND uq.tier = p_tier
      AND uq.period_type = 'monthly';
    
    -- Calculate remaining
    v_remaining := v_max_tokens - v_tokens_used;
    
    -- Return JSON result
    RETURN json_build_object(
        'allowed', v_remaining >= p_required_tokens,
        'tokens_remaining', v_remaining,
        'max_tokens', v_max_tokens,
        'tokens_used', v_tokens_used
    );
END;
$$ LANGUAGE plpgsql;

-- Trigger to create default token account for new users
CREATE OR REPLACE FUNCTION create_default_token_account()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO token_accounts (id, user_id, balance, tier, status, created_at, updated_at)
    VALUES (
        gen_random_uuid(),
        NEW.user_id,
        0,
        'Free',
        'active',
        CURRENT_TIMESTAMP,
        CURRENT_TIMESTAMP
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- VIEWS FOR REPORTING
-- ============================================================================

-- Token usage summary view
CREATE OR REPLACE VIEW v_token_usage_summary AS
SELECT
    ta.user_id,
    ta.tier,
    ta.balance AS current_balance,
    COUNT(tt.id) AS total_transactions,
    SUM(CASE WHEN tt.transaction_type = 'usage' THEN tt.amount ELSE 0 END) AS total_tokens_consumed,
    SUM(CASE WHEN tt.transaction_type = 'purchase' THEN tt.amount ELSE 0 END) AS total_tokens_purchased,
    MAX(tt.created_at) AS last_transaction_at
FROM token_accounts ta
LEFT JOIN token_transactions tt ON tt.token_account_id = ta.id
GROUP BY ta.id, ta.user_id, ta.tier;

-- Service usage breakdown view
CREATE OR REPLACE VIEW v_service_usage_breakdown AS
SELECT
    ta.user_id,
    tt.service_type,
    tt.modality,
    COUNT(tt.id) AS operation_count,
    SUM(tt.tokens_consumed) AS total_tokens,
    AVG(tt.estimated_cost_usd) AS avg_cost_usd,
    SUM(tt.estimated_cost_usd) AS total_cost_usd
FROM token_accounts ta
LEFT JOIN token_transactions tt ON tt.token_account_id = ta.id
WHERE tt.transaction_type = 'usage'
GROUP BY ta.id, ta.user_id, tt.service_type, tt.modality;

-- Daily usage tracking view
CREATE OR REPLACE VIEW v_daily_usage AS
SELECT
    DATE(tt.created_at) AS usage_date,
    tt.service_type,
    tt.modality,
    tt.user_id,
    COUNT(tt.id) AS operations_count,
    SUM(tt.tokens_consumed) AS total_tokens_consumed,
    SUM(tt.estimated_cost_usd) AS total_cost_usd
FROM token_transactions tt
WHERE tt.transaction_type = 'usage'
GROUP BY DATE(tt.created_at), tt.service_type, tt.modality, tt.user_id;

-- ============================================================================
-- MIGRATION VERION TRACKING
-- ============================================================================

CREATE TABLE IF NOT EXISTS schema_migrations (
    id SERIAL PRIMARY KEY,
    version VARCHAR(20) NOT NULL UNIQUE,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

INSERT INTO schema_migrations (version, applied_at, description) VALUES
    ('1.0.0', CURRENT_TIMESTAMP, 'Initial tokenized billing schema');

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE token_accounts IS 'Manages user token balances and subscription tiers';
COMMENT ON TABLE token_transactions IS 'Detailed log of all token movements (purchases, usage, refunds, bonuses)';
COMMENT ON TABLE token_packages IS 'Predefined token packages for purchase';
COMMENT ON TABLE usage_quotas IS 'Usage limits per tier and period (daily/monthly/annual)';
COMMENT ON TABLE provider_cost_rates IS 'Tracks costs per AI provider, model, and service type';
COMMENT ON TABLE model_preferences IS 'Stores user preferences for AI models and cost controls';
COMMENT ON TABLE token_usage_alerts IS 'Alerts for quota limits, cost anomalies, and usage patterns';

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================
