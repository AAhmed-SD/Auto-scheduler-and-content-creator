-- Create AI tables with proper relationships

-- Content Performance Metrics
CREATE TABLE IF NOT EXISTS public.content_performance_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_id UUID NOT NULL REFERENCES public.content(id) ON DELETE CASCADE,
    project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    engagement_rate DECIMAL,
    viral_score DECIMAL,
    performance_data JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- AI Learning Patterns
CREATE TABLE IF NOT EXISTS public.ai_learning_patterns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    content_id UUID REFERENCES public.content(id) ON DELETE CASCADE,
    pattern_type TEXT NOT NULL,
    pattern_data JSONB NOT NULL,
    success_rate DECIMAL,
    confidence_score DECIMAL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Content Style Analysis
CREATE TABLE IF NOT EXISTS public.content_style_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    content_id UUID NOT NULL REFERENCES public.content(id) ON DELETE CASCADE,
    style_elements JSONB NOT NULL,
    visual_features JSONB,
    text_features JSONB,
    effectiveness_score DECIMAL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Trend Analysis
CREATE TABLE IF NOT EXISTS public.trend_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,
    trend_data JSONB NOT NULL,
    relevance_score DECIMAL,
    start_date TIMESTAMPTZ,
    end_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT valid_platform CHECK (platform IN ('instagram', 'tiktok', 'twitter', 'linkedin', 'facebook'))
);

-- AI Improvement Tracking
CREATE TABLE IF NOT EXISTS public.ai_improvement_tracking (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    improvement_type TEXT NOT NULL,
    baseline_metrics JSONB,
    current_metrics JSONB,
    improvement_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_perf_metrics_content ON public.content_performance_metrics(content_id);
CREATE INDEX IF NOT EXISTS idx_perf_metrics_project ON public.content_performance_metrics(project_id);
CREATE INDEX IF NOT EXISTS idx_learning_patterns_project ON public.ai_learning_patterns(project_id);
CREATE INDEX IF NOT EXISTS idx_learning_patterns_content ON public.ai_learning_patterns(content_id);
CREATE INDEX IF NOT EXISTS idx_style_analysis_content ON public.content_style_analysis(content_id);
CREATE INDEX IF NOT EXISTS idx_style_analysis_project ON public.content_style_analysis(project_id);
CREATE INDEX IF NOT EXISTS idx_trend_platform ON public.trend_analysis(platform);
CREATE INDEX IF NOT EXISTS idx_trend_project ON public.trend_analysis(project_id);
CREATE INDEX IF NOT EXISTS idx_improvement_project ON public.ai_improvement_tracking(project_id);

-- Enable RLS
ALTER TABLE public.content_performance_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ai_learning_patterns ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.content_style_analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.trend_analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ai_improvement_tracking ENABLE ROW LEVEL SECURITY;

-- Add RLS policies for content_performance_metrics
CREATE POLICY "Users can view their AI metrics"
    ON public.content_performance_metrics FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM public.projects p
        WHERE p.id = content_performance_metrics.project_id
        AND (p.owner_id = auth.uid() OR auth.uid() = ANY(p.allowed_users))
    ));

CREATE POLICY "Users can insert AI metrics"
    ON public.content_performance_metrics FOR INSERT
    WITH CHECK (EXISTS (
        SELECT 1 FROM public.projects p
        WHERE p.id = project_id
        AND (p.owner_id = auth.uid() OR auth.uid() = ANY(p.allowed_users))
    ));

CREATE POLICY "Users can update AI metrics"
    ON public.content_performance_metrics FOR UPDATE
    USING (EXISTS (
        SELECT 1 FROM public.projects p
        WHERE p.id = content_performance_metrics.project_id
        AND (p.owner_id = auth.uid() OR auth.uid() = ANY(p.allowed_users))
    ));

-- Add RLS policies for ai_learning_patterns
CREATE POLICY "Users can view their AI patterns"
    ON public.ai_learning_patterns FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM public.projects p
        WHERE p.id = ai_learning_patterns.project_id
        AND (p.owner_id = auth.uid() OR auth.uid() = ANY(p.allowed_users))
    ));

CREATE POLICY "Users can insert AI patterns"
    ON public.ai_learning_patterns FOR INSERT
    WITH CHECK (EXISTS (
        SELECT 1 FROM public.projects p
        WHERE p.id = project_id
        AND (p.owner_id = auth.uid() OR auth.uid() = ANY(p.allowed_users))
    ));

CREATE POLICY "Users can update AI patterns"
    ON public.ai_learning_patterns FOR UPDATE
    USING (EXISTS (
        SELECT 1 FROM public.projects p
        WHERE p.id = ai_learning_patterns.project_id
        AND (p.owner_id = auth.uid() OR auth.uid() = ANY(p.allowed_users))
    ));

-- Add RLS policies for content_style_analysis
CREATE POLICY "Users can view their style analysis"
    ON public.content_style_analysis FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM public.projects p
        WHERE p.id = content_style_analysis.project_id
        AND (p.owner_id = auth.uid() OR auth.uid() = ANY(p.allowed_users))
    ));

CREATE POLICY "Users can insert style analysis"
    ON public.content_style_analysis FOR INSERT
    WITH CHECK (EXISTS (
        SELECT 1 FROM public.projects p
        WHERE p.id = project_id
        AND (p.owner_id = auth.uid() OR auth.uid() = ANY(p.allowed_users))
    ));

CREATE POLICY "Users can update style analysis"
    ON public.content_style_analysis FOR UPDATE
    USING (EXISTS (
        SELECT 1 FROM public.projects p
        WHERE p.id = content_style_analysis.project_id
        AND (p.owner_id = auth.uid() OR auth.uid() = ANY(p.allowed_users))
    ));

-- Add RLS policies for trend_analysis
CREATE POLICY "Users can view their trends"
    ON public.trend_analysis FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM public.projects p
        WHERE p.id = trend_analysis.project_id
        AND (p.owner_id = auth.uid() OR auth.uid() = ANY(p.allowed_users))
    ));

CREATE POLICY "Users can insert trends"
    ON public.trend_analysis FOR INSERT
    WITH CHECK (EXISTS (
        SELECT 1 FROM public.projects p
        WHERE p.id = project_id
        AND (p.owner_id = auth.uid() OR auth.uid() = ANY(p.allowed_users))
    ));

CREATE POLICY "Users can update trends"
    ON public.trend_analysis FOR UPDATE
    USING (EXISTS (
        SELECT 1 FROM public.projects p
        WHERE p.id = trend_analysis.project_id
        AND (p.owner_id = auth.uid() OR auth.uid() = ANY(p.allowed_users))
    ));

-- Add RLS policies for ai_improvement_tracking
CREATE POLICY "Users can view their improvements"
    ON public.ai_improvement_tracking FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM public.projects p
        WHERE p.id = ai_improvement_tracking.project_id
        AND (p.owner_id = auth.uid() OR auth.uid() = ANY(p.allowed_users))
    ));

CREATE POLICY "Users can insert improvements"
    ON public.ai_improvement_tracking FOR INSERT
    WITH CHECK (EXISTS (
        SELECT 1 FROM public.projects p
        WHERE p.id = project_id
        AND (p.owner_id = auth.uid() OR auth.uid() = ANY(p.allowed_users))
    ));

CREATE POLICY "Users can update improvements"
    ON public.ai_improvement_tracking FOR UPDATE
    USING (EXISTS (
        SELECT 1 FROM public.projects p
        WHERE p.id = ai_improvement_tracking.project_id
        AND (p.owner_id = auth.uid() OR auth.uid() = ANY(p.allowed_users))
    ));

-- Create optimize_content function
CREATE OR REPLACE FUNCTION public.optimize_content(
    p_content_id UUID,
    p_platform VARCHAR
)
RETURNS TABLE (
    optimization_suggestions JSONB,
    viral_potential DECIMAL,
    style_alignment DECIMAL,
    recommended_changes JSONB
) AS $$
DECLARE
    v_project_id UUID;
BEGIN
    -- Get project_id and verify access
    SELECT c.project_id INTO v_project_id
    FROM public.content c
    JOIN public.projects p ON p.id = c.project_id
    WHERE c.id = p_content_id
    AND (p.owner_id = auth.uid() OR auth.uid() = ANY(p.allowed_users));

    IF v_project_id IS NULL THEN
        RAISE EXCEPTION 'Content not found or access denied';
    END IF;

    RETURN QUERY
    WITH content_metrics AS (
        SELECT 
            c.id,
            c.project_id,
            c.content_data,
            cpm.engagement_rate,
            cpm.viral_score,
            csa.style_elements,
            csa.effectiveness_score,
            alp.pattern_data,
            alp.success_rate
        FROM public.content c
        LEFT JOIN public.content_performance_metrics cpm ON cpm.content_id = c.id
        LEFT JOIN public.content_style_analysis csa ON csa.content_id = c.id
        LEFT JOIN public.ai_learning_patterns alp ON alp.content_id = c.id
        WHERE c.id = p_content_id
    ),
    trend_data AS (
        SELECT 
            ta.trend_data,
            ta.relevance_score
        FROM public.trend_analysis ta
        WHERE ta.platform = p_platform
        AND ta.project_id = v_project_id
        ORDER BY ta.created_at DESC
        LIMIT 1
    )
    SELECT 
        jsonb_build_object(
            'content_type', p_platform,
            'engagement_opportunities', COALESCE(cm.pattern_data->'engagement_patterns', '[]'::jsonb),
            'trending_elements', COALESCE(td.trend_data->'current_trends', '[]'::jsonb),
            'style_recommendations', COALESCE(cm.style_elements->'recommendations', '[]'::jsonb)
        ) as optimization_suggestions,
        COALESCE(cm.viral_score, 0) as viral_potential,
        COALESCE(cm.effectiveness_score, 0) as style_alignment,
        jsonb_build_object(
            'visual_adjustments', COALESCE(cm.style_elements->'visual_adjustments', '[]'::jsonb),
            'text_improvements', COALESCE(cm.style_elements->'text_improvements', '[]'::jsonb),
            'timing_recommendations', COALESCE(td.trend_data->'optimal_timing', '{}')
        ) as recommended_changes
    FROM content_metrics cm
    LEFT JOIN trend_data td ON true;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER; 