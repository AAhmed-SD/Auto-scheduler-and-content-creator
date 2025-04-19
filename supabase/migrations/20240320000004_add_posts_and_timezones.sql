-- Add timezone to users table if not exists
ALTER TABLE auth.users ADD COLUMN IF NOT EXISTS timezone VARCHAR(50) DEFAULT 'UTC';

-- Create posts table
CREATE TABLE IF NOT EXISTS public.posts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    content_id UUID REFERENCES public.content(id) ON DELETE SET NULL,
    title TEXT,
    content TEXT,
    video_url TEXT,
    image_url TEXT,
    thumbnail_url TEXT,
    platform VARCHAR(50) NOT NULL,
    scheduled_time TIMESTAMPTZ NOT NULL,
    posted_at TIMESTAMPTZ,
    status VARCHAR(20) DEFAULT 'draft',
    retry_count INTEGER DEFAULT 0,
    last_attempt TIMESTAMPTZ,
    error_message TEXT,
    engagement_metrics JSONB DEFAULT '{}'::jsonb,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    CONSTRAINT valid_platform CHECK (platform IN ('instagram', 'tiktok', 'twitter', 'linkedin', 'facebook', 'threads')),
    CONSTRAINT valid_status CHECK (status IN ('draft', 'scheduled', 'processing', 'published', 'failed', 'cancelled', 'archived'))
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_posts_project ON public.posts(project_id);
CREATE INDEX IF NOT EXISTS idx_posts_platform ON public.posts(platform);
CREATE INDEX IF NOT EXISTS idx_posts_status ON public.posts(status);
CREATE INDEX IF NOT EXISTS idx_posts_scheduled_time ON public.posts(scheduled_time);
CREATE INDEX IF NOT EXISTS idx_posts_created_by ON public.posts(created_by);

-- Enable RLS
ALTER TABLE public.posts ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users can view posts in their projects" ON public.posts
    FOR SELECT USING (EXISTS (
        SELECT 1 FROM public.projects p
        WHERE p.id = posts.project_id
        AND (p.owner_id = auth.uid() OR auth.uid() = ANY(p.allowed_users))
    ));

CREATE POLICY "Users can manage posts in their projects" ON public.posts
    FOR ALL USING (EXISTS (
        SELECT 1 FROM public.projects p
        WHERE p.id = posts.project_id
        AND (p.owner_id = auth.uid() OR auth.uid() = ANY(p.allowed_users))
    ));

-- Create helper functions
CREATE OR REPLACE FUNCTION public.get_pending_posts(platform_param VARCHAR DEFAULT NULL)
RETURNS SETOF public.posts AS $$
BEGIN
    RETURN QUERY
    SELECT *
    FROM public.posts
    WHERE status = 'scheduled'
    AND scheduled_time <= NOW()
    AND deleted_at IS NULL
    AND (platform_param IS NULL OR platform = platform_param)
    ORDER BY scheduled_time ASC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to convert time between timezones
CREATE OR REPLACE FUNCTION public.convert_to_user_timezone(
    timestamp_utc TIMESTAMPTZ,
    user_timezone VARCHAR DEFAULT 'UTC'
)
RETURNS TIMESTAMPTZ AS $$
BEGIN
    RETURN timestamp_utc AT TIME ZONE user_timezone;
END;
$$ LANGUAGE plpgsql IMMUTABLE; 