-- Add viral prediction scoring and user preference learning

-- Viral Pattern Recognition
CREATE TABLE IF NOT EXISTS public.viral_patterns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE NOT NULL,
    platform VARCHAR(50) NOT NULL,
    pattern_signature JSONB NOT NULL, -- Stores unique identifiers of viral content
    success_metrics JSONB NOT NULL, -- Engagement rates, velocity, reach
    audience_response JSONB, -- Demographic breakdown of engagement
    time_factors JSONB, -- Best posting times, seasonal factors
    visual_elements JSONB, -- Color schemes, composition, movement patterns
    audio_elements JSONB, -- Sound patterns, music types, voice characteristics
    text_elements JSONB, -- Caption styles, hashtag patterns, call-to-actions
    contextual_factors JSONB, -- Current trends, events, cultural moments
    confidence_score DECIMAL(5,2), -- AI confidence in pattern
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- User Style Preferences
CREATE TABLE IF NOT EXISTS public.user_style_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE NOT NULL,
    style_profile JSONB NOT NULL, -- Visual, audio, and text preferences
    brand_guidelines JSONB, -- Brand-specific rules and preferences
    audience_segments JSONB, -- Target audience characteristics
    successful_elements JSONB, -- Previously successful content elements
    avoided_elements JSONB, -- Elements to avoid based on past performance
    seasonal_preferences JSONB, -- Time-based style variations
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Content Optimization Rules
CREATE TABLE IF NOT EXISTS public.content_optimization_rules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE NOT NULL,
    platform VARCHAR(50) NOT NULL,
    rule_type VARCHAR(50) NOT NULL,
    rule_definition JSONB NOT NULL, -- Specific optimization rules
    application_context JSONB, -- When to apply the rule
    priority INTEGER, -- Rule priority/importance
    success_rate DECIMAL(5,2), -- Rule effectiveness
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Drop the table if it exists to ensure clean creation
DROP TABLE IF EXISTS public.ai_decision_log;

-- AI Decision Log
CREATE TABLE public.ai_decision_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE NOT NULL,
    content_id UUID REFERENCES public.content(id) ON DELETE CASCADE,
    decision_type VARCHAR(50) NOT NULL,
    input_factors JSONB NOT NULL DEFAULT '{}',
    decision_output JSONB NOT NULL DEFAULT '{}',
    success_metrics JSONB DEFAULT '{}',
    learning_outcomes JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Add index for performance
CREATE INDEX IF NOT EXISTS idx_ai_decision_content ON public.ai_decision_log(content_id);
CREATE INDEX IF NOT EXISTS idx_ai_decision_project ON public.ai_decision_log(project_id);

-- Enable RLS
ALTER TABLE public.ai_decision_log ENABLE ROW LEVEL SECURITY;

-- Create advanced analytics views
CREATE OR REPLACE VIEW public.viral_potential_analysis AS
SELECT 
    c.id as content_id,
    c.project_id,
    c.title,
    vp.pattern_signature,
    vp.success_metrics,
    usp.style_profile,
    cor.rule_definition,
    -- Calculate viral potential score
    (
        COALESCE((vp.success_metrics->>'engagement_rate')::decimal, 0) * 0.4 +
        COALESCE((vp.success_metrics->>'growth_velocity')::decimal, 0) * 0.3 +
        COALESCE((vp.confidence_score), 0) * 0.3
    ) as viral_potential_score
FROM 
    public.content c
    LEFT JOIN public.viral_patterns vp ON c.project_id = vp.project_id
    LEFT JOIN public.user_style_preferences usp ON c.project_id = usp.project_id
    LEFT JOIN public.content_optimization_rules cor ON c.project_id = cor.project_id
WHERE 
    c.status = 'draft';

-- Create optimization function
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
    v_viral_patterns JSONB;
    v_style_preferences JSONB;
    v_optimization_rules JSONB;
BEGIN
    -- Get project_id
    SELECT project_id INTO v_project_id FROM public.content WHERE id = p_content_id;
    
    -- Get viral patterns
    SELECT 
        jsonb_agg(
            jsonb_build_object(
                'pattern', pattern_signature,
                'success_metrics', success_metrics,
                'confidence', confidence_score
            )
        )
    INTO v_viral_patterns 
    FROM public.viral_patterns 
    WHERE project_id = v_project_id AND platform = p_platform;
    
    -- Get style preferences
    SELECT 
        jsonb_build_object(
            'style_profile', style_profile,
            'brand_guidelines', brand_guidelines,
            'successful_elements', successful_elements
        )
    INTO v_style_preferences
    FROM public.user_style_preferences 
    WHERE project_id = v_project_id;
    
    -- Get optimization rules
    SELECT 
        jsonb_agg(
            jsonb_build_object(
                'rule', rule_definition,
                'priority', priority,
                'success_rate', success_rate
            )
        )
    INTO v_optimization_rules
    FROM public.content_optimization_rules 
    WHERE project_id = v_project_id AND platform = p_platform;
    
    -- Return optimization results
    RETURN QUERY 
    SELECT 
        jsonb_build_object(
            'viral_patterns', v_viral_patterns,
            'style_preferences', v_style_preferences,
            'optimization_rules', v_optimization_rules
        ),
        COALESCE((v_viral_patterns->0->>'confidence')::decimal, 0),
        COALESCE((v_style_preferences->'style_profile'->>'alignment')::decimal, 0),
        jsonb_build_object(
            'visual_adjustments', v_optimization_rules->0->'rule'->'visual',
            'text_adjustments', v_optimization_rules->0->'rule'->'text',
            'timing_adjustments', v_optimization_rules->0->'rule'->'timing'
        );
END;
$$ LANGUAGE plpgsql;

-- Add indexes
CREATE INDEX IF NOT EXISTS idx_viral_patterns_project_platform ON viral_patterns(project_id, platform);
CREATE INDEX IF NOT EXISTS idx_viral_patterns_confidence ON viral_patterns(confidence_score);
CREATE INDEX IF NOT EXISTS idx_user_preferences_project ON user_style_preferences(project_id);
CREATE INDEX IF NOT EXISTS idx_optimization_rules_project_platform ON content_optimization_rules(project_id, platform);

-- Enable RLS
ALTER TABLE public.viral_patterns ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_style_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.content_optimization_rules ENABLE ROW LEVEL SECURITY;

-- Add RLS Policies
DO $$ 
BEGIN
    -- Viral Patterns Policy
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE tablename = 'viral_patterns' 
        AND policyname = 'Users can access their project viral patterns'
    ) THEN
        CREATE POLICY "Users can access their project viral patterns"
            ON public.viral_patterns FOR ALL
            USING (EXISTS (
                SELECT 1 FROM public.projects p
                WHERE p.id = viral_patterns.project_id
                AND (p.owner_id = auth.uid() OR auth.uid() = ANY(p.allowed_users))
            ));
    END IF;

    -- Style Preferences Policy
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE tablename = 'user_style_preferences' 
        AND policyname = 'Users can access their project style preferences'
    ) THEN
        CREATE POLICY "Users can access their project style preferences"
            ON public.user_style_preferences FOR ALL
            USING (EXISTS (
                SELECT 1 FROM public.projects p
                WHERE p.id = user_style_preferences.project_id
                AND (p.owner_id = auth.uid() OR auth.uid() = ANY(p.allowed_users))
            ));
    END IF;

    -- Optimization Rules Policy
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE tablename = 'content_optimization_rules' 
        AND policyname = 'Users can access their project optimization rules'
    ) THEN
        CREATE POLICY "Users can access their project optimization rules"
            ON public.content_optimization_rules FOR ALL
            USING (EXISTS (
                SELECT 1 FROM public.projects p
                WHERE p.id = content_optimization_rules.project_id
                AND (p.owner_id = auth.uid() OR auth.uid() = ANY(p.allowed_users))
            ));
    END IF;

    -- AI Decision Log Policy
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE tablename = 'ai_decision_log' 
        AND policyname = 'Users can access their project AI decisions'
    ) THEN
        CREATE POLICY "Users can access their project AI decisions"
            ON public.ai_decision_log FOR ALL
            USING (EXISTS (
                SELECT 1 FROM public.projects p
                WHERE p.id = ai_decision_log.project_id
                AND (p.owner_id = auth.uid() OR auth.uid() = ANY(p.allowed_users))
            ));
    END IF;
END $$; 