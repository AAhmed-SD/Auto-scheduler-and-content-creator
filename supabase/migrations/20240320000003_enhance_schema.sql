-- Enhance schema with scheduling, caching, and analytics

-- Create scheduling table
CREATE TABLE IF NOT EXISTS public.schedules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    content_id UUID REFERENCES public.content(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,
    scheduled_time TIMESTAMPTZ NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    retry_count INTEGER DEFAULT 0,
    last_attempt TIMESTAMPTZ,
    error_message TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT valid_platform CHECK (platform IN ('instagram', 'tiktok', 'twitter', 'linkedin', 'facebook')),
    CONSTRAINT valid_status CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'cancelled'))
);

-- Create cache table
CREATE TABLE IF NOT EXISTS public.cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key TEXT NOT NULL UNIQUE,
    value JSONB NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create analytics table
CREATE TABLE IF NOT EXISTS public.analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    content_id UUID REFERENCES public.content(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value NUMERIC NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT valid_platform CHECK (platform IN ('instagram', 'tiktok', 'twitter', 'linkedin', 'facebook'))
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_schedules_project ON public.schedules(project_id);
CREATE INDEX IF NOT EXISTS idx_schedules_content ON public.schedules(content_id);
CREATE INDEX IF NOT EXISTS idx_schedules_time ON public.schedules(scheduled_time);
CREATE INDEX IF NOT EXISTS idx_schedules_status ON public.schedules(status);
CREATE INDEX IF NOT EXISTS idx_cache_key ON public.cache(key);
CREATE INDEX IF NOT EXISTS idx_cache_expires ON public.cache(expires_at);
CREATE INDEX IF NOT EXISTS idx_analytics_project ON public.analytics(project_id);
CREATE INDEX IF NOT EXISTS idx_analytics_content ON public.analytics(content_id);
CREATE INDEX IF NOT EXISTS idx_analytics_platform ON public.analytics(platform);
CREATE INDEX IF NOT EXISTS idx_analytics_metric ON public.analytics(metric_name);
CREATE INDEX IF NOT EXISTS idx_analytics_timestamp ON public.analytics(timestamp);

-- Enable RLS
ALTER TABLE public.schedules ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.cache ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analytics ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users can view schedules in their projects" ON public.schedules
    FOR SELECT USING (EXISTS (
        SELECT 1 FROM public.projects p
        WHERE p.id = schedules.project_id
        AND (p.owner_id = auth.uid() OR auth.uid() = ANY(p.allowed_users) OR p.is_private = false)
    ));

CREATE POLICY "Users can manage schedules in their projects" ON public.schedules
    FOR ALL USING (EXISTS (
        SELECT 1 FROM public.projects p
        WHERE p.id = schedules.project_id
        AND (p.owner_id = auth.uid() OR auth.uid() = ANY(p.allowed_users))
    ));

CREATE POLICY "Cache is publicly readable" ON public.cache
    FOR SELECT USING (true);

CREATE POLICY "Cache is writable by authenticated users" ON public.cache
    FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Users can view analytics in their projects" ON public.analytics
    FOR SELECT USING (EXISTS (
        SELECT 1 FROM public.projects p
        WHERE p.id = analytics.project_id
        AND (p.owner_id = auth.uid() OR auth.uid() = ANY(p.allowed_users) OR p.is_private = false)
    ));

CREATE POLICY "Users can insert analytics in their projects" ON public.analytics
    FOR INSERT WITH CHECK (EXISTS (
        SELECT 1 FROM public.projects p
        WHERE p.id = project_id
        AND (p.owner_id = auth.uid() OR auth.uid() = ANY(p.allowed_users))
    ));

-- Create functions
CREATE OR REPLACE FUNCTION public.cleanup_expired_cache()
RETURNS void AS $$
BEGIN
    DELETE FROM public.cache WHERE expires_at < NOW();
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create triggers
CREATE TRIGGER update_schedules_updated_at
    BEFORE UPDATE ON public.schedules
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_cache_updated_at
    BEFORE UPDATE ON public.cache
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column(); 