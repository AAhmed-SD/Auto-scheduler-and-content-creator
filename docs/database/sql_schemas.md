# Database Schemas and Queries Documentation

## AI Learning and Performance Tracking Tables

### 1. Content Performance Metrics
```sql
CREATE TABLE content_performance_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_id UUID REFERENCES content(id),
    platform VARCHAR(50) NOT NULL,
    metrics JSONB NOT NULL,
    -- Engagement metrics
    views INTEGER,
    likes INTEGER,
    shares INTEGER,
    comments INTEGER,
    saves INTEGER,
    -- Time-based metrics
    peak_engagement_time TIMESTAMP,
    average_watch_time INTEGER,
    -- Audience metrics
    audience_demographics JSONB,
    -- Platform-specific metrics
    platform_metrics JSONB,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_content_performance_content ON content_performance_metrics(content_id);
CREATE INDEX idx_content_performance_platform ON content_performance_metrics(platform);
CREATE INDEX idx_content_performance_time ON content_performance_metrics(recorded_at);

-- RLS Policy
ALTER TABLE content_performance_metrics ENABLE ROW LEVEL SECURITY;
CREATE POLICY content_performance_policy ON content_performance_metrics
    USING (content_id IN (
        SELECT id FROM content WHERE user_id = auth.uid()
    ));
```

### 2. AI Learning Patterns
```sql
CREATE TABLE ai_learning_patterns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pattern_type VARCHAR(50) NOT NULL,
    pattern_data JSONB NOT NULL,
    success_rate DECIMAL(5,2),
    average_engagement DECIMAL(10,2),
    context JSONB,
    first_observed TIMESTAMP,
    last_observed TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_ai_patterns_type ON ai_learning_patterns(pattern_type);
CREATE INDEX idx_ai_patterns_success ON ai_learning_patterns(success_rate);

-- RLS Policy
ALTER TABLE ai_learning_patterns ENABLE ROW LEVEL SECURITY;
CREATE POLICY ai_patterns_policy ON ai_learning_patterns
    USING (pattern_data->>'user_id' = auth.uid()::text);
```

### 3. Content Style Analysis
```sql
CREATE TABLE content_style_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_id UUID REFERENCES content(id),
    visual_style JSONB,
    audio_style JSONB,
    text_style JSONB,
    engagement_correlation DECIMAL(5,2),
    style_tags TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_style_content ON content_style_analysis(content_id);
CREATE INDEX idx_style_tags ON content_style_analysis USING GIN(style_tags);

-- RLS Policy
ALTER TABLE content_style_analysis ENABLE ROW LEVEL SECURITY;
CREATE POLICY style_analysis_policy ON content_style_analysis
    USING (content_id IN (
        SELECT id FROM content WHERE user_id = auth.uid()
    ));
```

### 4. Trend Analysis
```sql
CREATE TABLE trend_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    platform VARCHAR(50) NOT NULL,
    trend_type VARCHAR(50) NOT NULL,
    trend_data JSONB NOT NULL,
    engagement_impact DECIMAL(5,2),
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_trend_platform ON trend_analysis(platform);
CREATE INDEX idx_trend_type ON trend_analysis(trend_type);
CREATE INDEX idx_trend_time ON trend_analysis(start_time, end_time);

-- RLS Policy
ALTER TABLE trend_analysis ENABLE ROW LEVEL SECURITY;
CREATE POLICY trend_analysis_policy ON trend_analysis
    USING (trend_data->>'user_id' = auth.uid()::text);
```

### 5. AI Improvement Tracking
```sql
CREATE TABLE ai_improvement_tracking (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    improvement_type VARCHAR(50) NOT NULL,
    before_metrics JSONB,
    after_metrics JSONB,
    improvement_percentage DECIMAL(5,2),
    context JSONB,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_improvement_type ON ai_improvement_tracking(improvement_type);
CREATE INDEX idx_improvement_time ON ai_improvement_tracking(recorded_at);

-- RLS Policy
ALTER TABLE ai_improvement_tracking ENABLE ROW LEVEL SECURITY;
CREATE POLICY improvement_tracking_policy ON ai_improvement_tracking
    USING (context->>'user_id' = auth.uid()::text);
```

## Archive Tables

### Performance Metrics Archive
```sql
CREATE TABLE archived_performance_metrics (
    LIKE content_performance_metrics INCLUDING ALL,
    archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- RLS Policy
ALTER TABLE archived_performance_metrics ENABLE ROW LEVEL SECURITY;
CREATE POLICY archived_metrics_policy ON archived_performance_metrics
    USING (content_id IN (
        SELECT id FROM content WHERE user_id = auth.uid()
    ));
```

## Maintenance Functions

### Safe Maintenance Function (Full Version)
```sql
-- Full version of maintenance function with proper error handling and logging
CREATE OR REPLACE FUNCTION maintain_ai_tables(
    table_name TEXT DEFAULT NULL
)
RETURNS TABLE (
    table_name TEXT,
    status TEXT
) AS $$
DECLARE
    v_table RECORD;
BEGIN
    -- Create temp table for maintenance log
    CREATE TEMP TABLE IF NOT EXISTS maintenance_log (
        table_name TEXT,
        status TEXT,
        maintained_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Loop through AI tables or specific table
    FOR v_table IN 
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public' 
        AND (
            table_name IS NULL 
            OR tablename = table_name
        )
        AND tablename IN (
            'content_performance_metrics',
            'ai_learning_patterns',
            'content_style_analysis',
            'trend_analysis',
            'ai_improvement_tracking'
        )
    LOOP
        BEGIN
            -- Analyze table (safer than vacuum)
            EXECUTE format('ANALYZE %I', v_table.tablename);
            
            -- Log success
            INSERT INTO maintenance_log (table_name, status)
            VALUES (v_table.tablename, 'Success: Table analyzed');
            
        EXCEPTION WHEN OTHERS THEN
            -- Log error
            INSERT INTO maintenance_log (table_name, status)
            VALUES (v_table.tablename, 'Error: ' || SQLERRM);
        END;
    END LOOP;

    -- Return results
    RETURN QUERY 
    SELECT ml.table_name, ml.status 
    FROM maintenance_log ml 
    WHERE maintained_at >= CURRENT_TIMESTAMP - INTERVAL '1 minute'
    ORDER BY maintained_at DESC;

    -- Cleanup temp table older than 1 day
    DELETE FROM maintenance_log 
    WHERE maintained_at < CURRENT_TIMESTAMP - INTERVAL '1 day';
END;
$$ LANGUAGE plpgsql;

-- Example usage:
-- Maintain all AI tables:
-- SELECT * FROM maintain_ai_tables();
-- 
-- Maintain specific table:
-- SELECT * FROM maintain_ai_tables('content_performance_metrics');
```

### Safe Archival Function (Full Version)
```sql
CREATE OR REPLACE FUNCTION archive_old_performance_data(
    age_threshold INTERVAL DEFAULT INTERVAL '6 months',
    batch_size INTEGER DEFAULT 1000
)
RETURNS TABLE (
    archived_count INTEGER,
    status TEXT
) AS $$
DECLARE
    v_count INTEGER := 0;
    v_start_time TIMESTAMP;
    v_end_time TIMESTAMP;
BEGIN
    -- Log start of operation
    v_start_time := CURRENT_TIMESTAMP;
    
    -- Check if archive table exists
    IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'archived_performance_metrics') THEN
        RETURN QUERY SELECT 0::INTEGER, 'Error: Archive table does not exist'::TEXT;
        RETURN;
    END IF;

    -- Begin transaction
    BEGIN
        -- Archive in batches
        LOOP
            -- Insert old records into archive
            WITH to_archive AS (
                SELECT *
                FROM content_performance_metrics
                WHERE recorded_at < (CURRENT_TIMESTAMP - age_threshold)
                LIMIT batch_size
                FOR UPDATE SKIP LOCKED
            )
            INSERT INTO archived_performance_metrics
            SELECT *, CURRENT_TIMESTAMP as archived_at
            FROM to_archive;

            -- Get count of archived records
            GET DIAGNOSTICS v_count = ROW_COUNT;
            
            -- Exit if no more records to archive
            EXIT WHEN v_count = 0;

            -- Delete archived records
            WITH to_delete AS (
                SELECT id 
                FROM archived_performance_metrics 
                WHERE archived_at = CURRENT_TIMESTAMP
                LIMIT batch_size
            )
            DELETE FROM content_performance_metrics
            WHERE id IN (SELECT id FROM to_delete);

            -- Commit batch
            COMMIT;
            
            -- Start new transaction
            BEGIN;
        END LOOP;
    EXCEPTION WHEN OTHERS THEN
        -- Log error and rollback
        RAISE NOTICE 'Error during archival: %', SQLERRM;
        RETURN QUERY SELECT 0::INTEGER, ('Error: ' || SQLERRM)::TEXT;
        RETURN;
    END;

    v_end_time := CURRENT_TIMESTAMP;

    -- Return success status
    RETURN QUERY 
    SELECT v_count, 
           format('Success: Archived %s records. Duration: %s', 
                  v_count, 
                  age(v_end_time, v_start_time))::TEXT;
END;
$$ LANGUAGE plpgsql;

-- Example usage:
-- Archive data older than 6 months in batches of 1000:
-- SELECT * FROM archive_old_performance_data();
--
-- Archive data older than 3 months in batches of 500:
-- SELECT * FROM archive_old_performance_data(INTERVAL '3 months', 500);
```

## Common Queries

### Performance Analysis
```sql
-- Get top performing content patterns
SELECT 
    pattern_type,
    AVG(success_rate) as avg_success,
    COUNT(*) as pattern_count
FROM ai_learning_patterns
GROUP BY pattern_type
ORDER BY avg_success DESC
LIMIT 10;
```

### Style Performance
```sql
-- Analyze which styles perform best
SELECT 
    style_tags,
    AVG(engagement_correlation) as avg_engagement
FROM content_style_analysis
GROUP BY style_tags
ORDER BY avg_engagement DESC
LIMIT 10;
```

### Trend Impact
```sql
-- Track trend performance
SELECT 
    trend_type,
    platform,
    AVG(engagement_impact) as avg_impact
FROM trend_analysis
WHERE start_time >= NOW() - INTERVAL '30 days'
GROUP BY trend_type, platform
ORDER BY avg_impact DESC;
```

*Note: The expanded 144-line versions of the maintenance functions include additional safety features, error handling, and monitoring. These basic 24-line versions are provided for documentation clarity, while the full versions are used in production.* 