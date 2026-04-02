-- ============================================================================
-- AI Content Localization Platform - Database Schema (SQL)
-- Generated from SQLAlchemy ORM Models
-- ============================================================================

-- ============================================================================
-- USERS TABLE
-- ============================================================================
CREATE TABLE users (
    user_id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100),
    api_key VARCHAR(255) UNIQUE,
    subscription_tier VARCHAR(20) NOT NULL DEFAULT 'free',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_email ON users(email);
CREATE INDEX idx_user_api_key ON users(api_key);
CREATE INDEX idx_user_created_at ON users(created_at);


-- ============================================================================
-- LOCALIZATION_HISTORY TABLE
-- ============================================================================
CREATE TABLE localization_history (
    request_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    source_text TEXT NOT NULL,
    source_language VARCHAR(10) NOT NULL DEFAULT 'en',
    target_language VARCHAR(10) NOT NULL,
    tone VARCHAR(20) NOT NULL,
    localized_text TEXT NOT NULL,
    explanation TEXT,
    detected_sentiment VARCHAR(20),
    quality_score FLOAT NOT NULL,
    character_count INTEGER NOT NULL,
    word_count INTEGER NOT NULL,
    execution_time_ms INTEGER NOT NULL,
    model_used VARCHAR(50) NOT NULL,
    idioms_detected INTEGER NOT NULL DEFAULT 0,
    idioms_replaced INTEGER NOT NULL DEFAULT 0,
    cultural_adaptations_applied JSON,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE INDEX idx_localization_user_id ON localization_history(user_id);
CREATE INDEX idx_localization_target_lang ON localization_history(target_language);
CREATE INDEX idx_localization_tone ON localization_history(tone);
CREATE INDEX idx_localization_quality_score ON localization_history(quality_score);
CREATE INDEX idx_localization_created_at ON localization_history(created_at);
CREATE INDEX idx_localization_composite ON localization_history(user_id, created_at);


-- ============================================================================
-- CULTURAL_ADAPTATIONS TABLE
-- ============================================================================
CREATE TABLE cultural_adaptations (
    adaptation_id VARCHAR(36) PRIMARY KEY,
    request_id VARCHAR(36) NOT NULL,
    source_idiom VARCHAR(255) NOT NULL,
    target_idiom VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL,
    equivalence_type VARCHAR(20) NOT NULL,
    semantic_preservation FLOAT NOT NULL,
    confidence_score FLOAT NOT NULL,
    explanation TEXT,
    source_language VARCHAR(10) NOT NULL,
    target_language VARCHAR(10) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (request_id) REFERENCES localization_history(request_id) ON DELETE CASCADE
);

CREATE INDEX idx_adaptation_request_id ON cultural_adaptations(request_id);
CREATE INDEX idx_adaptation_category ON cultural_adaptations(category);
CREATE INDEX idx_adaptation_equivalence ON cultural_adaptations(equivalence_type);


-- ============================================================================
-- FEEDBACK TABLE
-- ============================================================================
CREATE TABLE feedback (
    feedback_id VARCHAR(36) PRIMARY KEY,
    request_id VARCHAR(36) UNIQUE NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    rating INTEGER NOT NULL,
    comment TEXT,
    aspects JSON,
    helpful BOOLEAN,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (request_id) REFERENCES localization_history(request_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    UNIQUE (request_id, user_id)
);

CREATE INDEX idx_feedback_request_id ON feedback(request_id);
CREATE INDEX idx_feedback_user_id ON feedback(user_id);
CREATE INDEX idx_feedback_rating ON feedback(rating);
CREATE INDEX idx_feedback_created_at ON feedback(created_at);


-- ============================================================================
-- ANALYTICS TABLE
-- ============================================================================
CREATE TABLE analytics (
    metric_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36),
    metric_date TIMESTAMP NOT NULL,
    total_requests INTEGER NOT NULL DEFAULT 0,
    total_characters INTEGER NOT NULL DEFAULT 0,
    total_words INTEGER NOT NULL DEFAULT 0,
    avg_quality_score FLOAT NOT NULL,
    avg_execution_time_ms FLOAT NOT NULL,
    languages_used JSON,
    tones_used JSON,
    top_language VARCHAR(10),
    top_tone VARCHAR(20),
    feedback_count INTEGER NOT NULL DEFAULT 0,
    avg_rating FLOAT,
    cultural_adaptations_applied INTEGER NOT NULL DEFAULT 0,
    idioms_detected_avg FLOAT NOT NULL DEFAULT 0.0,
    error_count INTEGER NOT NULL DEFAULT 0,
    success_rate FLOAT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE INDEX idx_analytics_user_id ON analytics(user_id);
CREATE INDEX idx_analytics_metric_date ON analytics(metric_date);
CREATE INDEX idx_analytics_composite ON analytics(user_id, metric_date);


-- ============================================================================
-- LANGUAGE_METADATA TABLE
-- ============================================================================
CREATE TABLE language_metadata (
    lang_code VARCHAR(10) PRIMARY KEY,
    language_name VARCHAR(100) NOT NULL,
    native_name VARCHAR(100) NOT NULL,
    region_code VARCHAR(10),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    native_speakers INTEGER,
    linguistic_family VARCHAR(50),
    complexity_score INTEGER NOT NULL,
    supported_idioms INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================================
-- TONE_PROFILES TABLE
-- ============================================================================
CREATE TABLE tone_profiles (
    tone_id VARCHAR(36) PRIMARY KEY,
    tone_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT NOT NULL,
    characteristics JSON,
    system_prompt TEXT NOT NULL,
    example_output TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tone_name ON tone_profiles(tone_name);


-- ============================================================================
-- USAGE_QUOTAS TABLE
-- ============================================================================
CREATE TABLE usage_quotas (
    user_id VARCHAR(36) PRIMARY KEY,
    requests_this_month INTEGER NOT NULL DEFAULT 0,
    characters_this_month INTEGER NOT NULL DEFAULT 0,
    quota_limit_requests INTEGER NOT NULL,
    quota_limit_characters INTEGER NOT NULL,
    reset_date TIMESTAMP NOT NULL,
    last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);


-- ============================================================================
-- API_LOGS TABLE
-- ============================================================================
CREATE TABLE api_logs (
    log_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36),
    endpoint VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INTEGER NOT NULL,
    response_time_ms INTEGER NOT NULL,
    error_message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE INDEX idx_api_log_user_id ON api_logs(user_id);
CREATE INDEX idx_api_log_endpoint ON api_logs(endpoint);
CREATE INDEX idx_api_log_created_at ON api_logs(created_at);


-- ============================================================================
-- INITIAL DATA POPULATION
-- ============================================================================

-- Insert supported languages
INSERT INTO language_metadata (lang_code, language_name, native_name, region_code, is_active, complexity_score, supported_idioms) VALUES
('en', 'English', 'English', 'GB', TRUE, 6, 40),
('es', 'Spanish', 'Español', 'ES', TRUE, 6, 35),
('fr', 'French', 'Français', 'FR', TRUE, 7, 30),
('de', 'German', 'Deutsch', 'DE', TRUE, 8, 25),
('it', 'Italian', 'Italiano', 'IT', TRUE, 6, 20),
('pt', 'Portuguese', 'Português', 'PT', TRUE, 6, 20),
('hi', 'Hindi', 'हिन्दी', 'IN', TRUE, 9, 30),
('zh', 'Chinese', '中文', 'CN', TRUE, 10, 35),
('ja', 'Japanese', '日本語', 'JP', TRUE, 10, 35),
('ar', 'Arabic', 'العربية', 'SA', TRUE, 9, 25),
('ru', 'Russian', 'Русский', 'RU', TRUE, 8, 20),
('ko', 'Korean', '한국어', 'KR', TRUE, 8, 20);

-- Insert tone profiles
INSERT INTO tone_profiles (tone_id, tone_name, description, is_active) VALUES
('formal-001', 'formal', 'Professional, business-appropriate language', TRUE),
('casual-002', 'casual', 'Conversational, friendly tone', TRUE),
('market-003', 'marketing', 'Persuasive, sales-oriented language', TRUE),
('tech-004', 'technical', 'Technical, precise terminology', TRUE),
('neutral-005', 'neutral', 'Balanced, objective tone', TRUE);

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- User statistics view
CREATE VIEW user_statistics AS
SELECT
    u.user_id,
    u.email,
    u.subscription_tier,
    COUNT(DISTINCT lh.request_id) as total_requests,
    SUM(lh.character_count) as total_characters_processed,
    ROUND(AVG(lh.quality_score), 2) as avg_quality_score,
    COUNT(DISTINCT f.feedback_id) as feedback_count,
    ROUND(AVG(f.rating), 2) as avg_rating,
    u.created_at
FROM users u
LEFT JOIN localization_history lh ON u.user_id = lh.user_id
LEFT JOIN feedback f ON lh.request_id = f.request_id
GROUP BY u.user_id, u.email, u.subscription_tier, u.created_at;

-- Language usage view
CREATE VIEW language_usage AS
SELECT
    target_language,
    COUNT(*) as request_count,
    ROUND(AVG(quality_score), 2) as avg_quality,
    SUM(character_count) as total_characters,
    COUNT(DISTINCT user_id) as unique_users,
    DATE(created_at) as usage_date
FROM localization_history
GROUP BY target_language, DATE(created_at);

-- Quality metrics view
CREATE VIEW quality_metrics AS
SELECT
    DATE(created_at) as metric_date,
    COUNT(*) as total_requests,
    ROUND(AVG(quality_score), 2) as avg_quality,
    MIN(quality_score) as min_quality,
    MAX(quality_score) as max_quality,
    ROUND(AVG(execution_time_ms), 2) as avg_execution_time,
    SUM(idioms_replaced) as idioms_replaced_total,
    COUNT(CASE WHEN quality_score >= 80 THEN 1 END) as high_quality_count,
    ROUND(COUNT(CASE WHEN quality_score >= 80 THEN 1 END) * 100.0 / COUNT(*), 1) as success_rate_pct
FROM localization_history
GROUP BY DATE(created_at);

-- ============================================================================
-- END OF SCHEMA DEFINITION
-- ============================================================================

-- Statistics
-- Total tables: 9
-- Total relationships: 13
-- Total indexes: 35+
-- Views: 3
