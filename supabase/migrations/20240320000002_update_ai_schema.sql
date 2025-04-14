-- Add missing columns and relationships to existing AI tables
DO $$ 
BEGIN
    -- Add project_id to content_performance_metrics if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'content_performance_metrics' 
        AND column_name = 'project_id'
    ) THEN
        ALTER TABLE public.content_performance_metrics 
        ADD COLUMN project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE;
    END IF;

    -- Add project_id to ai_learning_patterns if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'ai_learning_patterns' 
        AND column_name = 'project_id'
    ) THEN
        ALTER TABLE public.ai_learning_patterns 
        ADD COLUMN project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE;
    END IF;

    -- Add project_id to content_style_analysis if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'content_style_analysis' 
        AND column_name = 'project_id'
    ) THEN
        ALTER TABLE public.content_style_analysis 
        ADD COLUMN project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE;
    END IF;

    -- Add project_id to trend_analysis if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'trend_analysis' 
        AND column_name = 'project_id'
    ) THEN
        ALTER TABLE public.trend_analysis 
        ADD COLUMN project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE;
    END IF;

    -- Add project_id to ai_improvement_tracking if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'ai_improvement_tracking' 
        AND column_name = 'project_id'
    ) THEN
        ALTER TABLE public.ai_improvement_tracking 
        ADD COLUMN project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE;
    END IF;
END $$;

-- Create missing indexes safely
DO $$ 
BEGIN
    -- Content Performance Metrics indexes
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_content_performance_project') THEN
        CREATE INDEX idx_content_performance_project ON content_performance_metrics(project_id);
    END IF;

    -- AI Learning Patterns indexes
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_ai_patterns_project') THEN
        CREATE INDEX idx_ai_patterns_project ON ai_learning_patterns(project_id);
    END IF;

    -- Content Style Analysis indexes
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_style_project') THEN
        CREATE INDEX idx_style_project ON content_style_analysis(project_id);
    END IF;

    -- Trend Analysis indexes
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_trend_project') THEN
        CREATE INDEX idx_trend_project ON trend_analysis(project_id);
    END IF;

    -- AI Improvement Tracking indexes
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_improvement_project') THEN
        CREATE INDEX idx_improvement_project ON ai_improvement_tracking(project_id);
    END IF;
END $$;

-- Update RLS policies safely
DO $$ 
BEGIN
    -- Create or update policies only if they don't exist
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE policyname = 'Users can view AI metrics for their projects' 
        AND tablename = 'content_performance_metrics'
    ) THEN
        CREATE POLICY "Users can view AI metrics for their projects"
            ON public.content_performance_metrics FOR SELECT
            USING (EXISTS (
                SELECT 1 FROM public.projects p
                WHERE p.id = content_performance_metrics.project_id
                AND (p.owner_id = auth.uid() OR auth.uid() = ANY(p.allowed_users))
            ));
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE policyname = 'Users can view AI patterns for their projects' 
        AND tablename = 'ai_learning_patterns'
    ) THEN
        CREATE POLICY "Users can view AI patterns for their projects"
            ON public.ai_learning_patterns FOR SELECT
            USING (EXISTS (
                SELECT 1 FROM public.projects p
                WHERE p.id = ai_learning_patterns.project_id
                AND (p.owner_id = auth.uid() OR auth.uid() = ANY(p.allowed_users))
            ));
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE policyname = 'Users can view style analysis for their projects' 
        AND tablename = 'content_style_analysis'
    ) THEN
        CREATE POLICY "Users can view style analysis for their projects"
            ON public.content_style_analysis FOR SELECT
            USING (EXISTS (
                SELECT 1 FROM public.projects p
                WHERE p.id = content_style_analysis.project_id
                AND (p.owner_id = auth.uid() OR auth.uid() = ANY(p.allowed_users))
            ));
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE policyname = 'Users can view trends for their projects' 
        AND tablename = 'trend_analysis'
    ) THEN
        CREATE POLICY "Users can view trends for their projects"
            ON public.trend_analysis FOR SELECT
            USING (EXISTS (
                SELECT 1 FROM public.projects p
                WHERE p.id = trend_analysis.project_id
                AND (p.owner_id = auth.uid() OR auth.uid() = ANY(p.allowed_users))
            ));
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE policyname = 'Users can view AI improvements for their projects' 
        AND tablename = 'ai_improvement_tracking'
    ) THEN
        CREATE POLICY "Users can view AI improvements for their projects"
            ON public.ai_improvement_tracking FOR SELECT
            USING (EXISTS (
                SELECT 1 FROM public.projects p
                WHERE p.id = ai_improvement_tracking.project_id
                AND (p.owner_id = auth.uid() OR auth.uid() = ANY(p.allowed_users))
            ));
    END IF;
END $$;

-- Ensure RLS is enabled (this is idempotent and safe)
ALTER TABLE public.content_performance_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ai_learning_patterns ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.content_style_analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.trend_analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ai_improvement_tracking ENABLE ROW LEVEL SECURITY; 