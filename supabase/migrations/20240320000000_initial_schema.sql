-- Create auth schema and tables first
CREATE SCHEMA IF NOT EXISTS auth;
CREATE SCHEMA IF NOT EXISTS storage;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create auth function (temporary for local development)
CREATE OR REPLACE FUNCTION auth.uid() RETURNS uuid AS $$
BEGIN
  RETURN '00000000-0000-0000-0000-000000000000'::uuid;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION auth.role() RETURNS text AS $$
BEGIN
  RETURN 'authenticated';
END;
$$ LANGUAGE plpgsql;

-- Create auth.users table (if not exists)
CREATE TABLE IF NOT EXISTS auth.users (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  email text UNIQUE NOT NULL
);

-- Create users table
CREATE TABLE IF NOT EXISTS public.users (
  id uuid PRIMARY KEY REFERENCES auth.users ON DELETE CASCADE,
  email text UNIQUE NOT NULL,
  full_name text,
  avatar_url text,
  created_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL,
  updated_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Create projects table
CREATE TABLE IF NOT EXISTS public.projects (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  name text NOT NULL,
  description text,
  owner_id uuid REFERENCES public.users ON DELETE CASCADE NOT NULL,
  is_private boolean DEFAULT true,
  allowed_users uuid[] DEFAULT array[]::uuid[],
  settings jsonb DEFAULT '{}'::jsonb,
  created_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL,
  updated_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Create project_members table
CREATE TABLE IF NOT EXISTS public.project_members (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  role TEXT NOT NULL DEFAULT 'member',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  CONSTRAINT unique_project_member UNIQUE (project_id, user_id),
  CONSTRAINT valid_role CHECK (role IN ('owner', 'admin', 'member', 'viewer'))
);

-- Create content table
CREATE TABLE IF NOT EXISTS public.content (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  description TEXT,
  content_type VARCHAR(50) NOT NULL,
  status VARCHAR(20) DEFAULT 'draft',
  content_data JSONB NOT NULL DEFAULT '{}'::jsonb,
  metadata JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  scheduled_for TIMESTAMPTZ,
  published_at TIMESTAMPTZ,
  created_by UUID REFERENCES auth.users(id),
  version INTEGER DEFAULT 1,
  CONSTRAINT valid_content_type CHECK (content_type IN ('instagram', 'tiktok', 'twitter', 'linkedin', 'facebook'))
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_project_members_project ON public.project_members(project_id);
CREATE INDEX IF NOT EXISTS idx_project_members_user ON public.project_members(user_id);
CREATE INDEX IF NOT EXISTS idx_content_project_id ON public.content(project_id);
CREATE INDEX IF NOT EXISTS idx_content_status ON public.content(status);
CREATE INDEX IF NOT EXISTS idx_content_type ON public.content(content_type);
CREATE INDEX IF NOT EXISTS idx_content_scheduled ON public.content(scheduled_for) WHERE scheduled_for IS NOT NULL;

-- Enable RLS
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.project_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.content ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users can view their own data" ON public.users
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can view their own or public projects" ON public.projects
  FOR SELECT USING (owner_id = auth.uid() OR auth.uid() = any(allowed_users) OR is_private = false);

CREATE POLICY "Users can create projects" ON public.projects
  FOR INSERT WITH CHECK (auth.uid() = owner_id);

CREATE POLICY "Project owners can update their projects" ON public.projects
  FOR UPDATE USING (auth.uid() = owner_id);

CREATE POLICY "Project owners can delete their projects" ON public.projects
  FOR DELETE USING (auth.uid() = owner_id);

CREATE POLICY "Project owners can manage members" ON public.project_members
  FOR ALL USING (EXISTS (
    SELECT 1 FROM public.projects p
    WHERE p.id = project_members.project_id
    AND p.owner_id = auth.uid()
  ));

CREATE POLICY "Users can view project members" ON public.project_members
  FOR SELECT USING (EXISTS (
    SELECT 1 FROM public.projects p
    WHERE p.id = project_members.project_id
    AND (p.owner_id = auth.uid() OR auth.uid() = ANY(p.allowed_users) OR p.is_private = false)
  ));

CREATE POLICY "Users can view content in their projects" ON public.content
  FOR SELECT USING (EXISTS (
    SELECT 1 FROM public.projects p
    WHERE p.id = content.project_id
    AND (p.owner_id = auth.uid() OR auth.uid() = ANY(p.allowed_users) OR p.is_private = false)
  ));

CREATE POLICY "Users can insert content in their projects" ON public.content
  FOR INSERT WITH CHECK (EXISTS (
    SELECT 1 FROM public.projects p
    WHERE p.id = project_id
    AND (p.owner_id = auth.uid() OR auth.uid() = ANY(p.allowed_users))
  ));

CREATE POLICY "Users can update content in their projects" ON public.content
  FOR UPDATE USING (EXISTS (
    SELECT 1 FROM public.projects p
    WHERE p.id = content.project_id
    AND (p.owner_id = auth.uid() OR auth.uid() = ANY(p.allowed_users))
  ));

-- Create functions
CREATE OR REPLACE FUNCTION public.handle_new_project()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.project_members (project_id, user_id, role)
  VALUES (NEW.id, NEW.owner_id, 'owner');
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers
CREATE TRIGGER on_project_created
  AFTER INSERT ON public.projects
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_new_project();

CREATE TRIGGER update_content_updated_at
  BEFORE UPDATE ON public.content
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

-- Create storage buckets
CREATE TABLE IF NOT EXISTS storage.buckets (
  id text PRIMARY KEY,
  name text NOT NULL,
  public boolean DEFAULT false
);

CREATE TABLE IF NOT EXISTS storage.objects (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  bucket_id text NOT NULL REFERENCES storage.buckets(id),
  name text NOT NULL,
  owner uuid NOT NULL REFERENCES auth.users(id),
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now(),
  last_accessed_at timestamptz DEFAULT now(),
  metadata jsonb DEFAULT '{}'::jsonb,
  path_tokens text[],
  CONSTRAINT unique_object_name UNIQUE (bucket_id, name)
);

-- Insert default storage bucket
INSERT INTO storage.buckets (id, name, public)
VALUES ('media', 'media', true)
ON CONFLICT (id) DO NOTHING;

-- Create storage policies
CREATE POLICY "Allow public read access" ON storage.objects
  FOR SELECT USING (bucket_id = 'media' AND auth.role() = 'authenticated');

CREATE POLICY "Allow authenticated uploads" ON storage.objects
  FOR INSERT WITH CHECK (bucket_id = 'media' AND auth.role() = 'authenticated');

CREATE POLICY "Allow individual ownership" ON storage.objects
  FOR UPDATE USING (auth.uid() = owner);

CREATE POLICY "Allow individual delete" ON storage.objects
  FOR DELETE USING (auth.uid() = owner);

-- Create media table
create table public.media (
  id uuid default uuid_generate_v4() primary key,
  user_id uuid references public.users on delete cascade not null,
  content_id uuid references public.content on delete cascade,
  file_name text not null,
  file_type text not null,
  file_size bigint not null,
  storage_path text not null,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create analytics table
create table public.analytics (
  id uuid default uuid_generate_v4() primary key,
  content_id uuid references public.content on delete cascade not null,
  platform text not null,
  views bigint default 0,
  likes bigint default 0,
  shares bigint default 0,
  comments bigint default 0,
  engagement_rate decimal,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create social media accounts table
create table public.social_media_accounts (
  id uuid default uuid_generate_v4() primary key,
  project_id uuid references public.projects on delete cascade not null,
  platform text not null,
  account_name text not null,
  account_id text not null,
  credentials jsonb not null,
  metadata jsonb,
  is_active boolean default true,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  updated_at timestamp with time zone default timezone('utc'::text, now()) not null,
  last_sync_at timestamp with time zone,
  constraint unique_account_per_platform_project unique (project_id, platform, account_id)
);

-- Create schedules table
create table public.schedules (
  id uuid default uuid_generate_v4() primary key,
  content_id uuid references public.content on delete cascade not null,
  social_account_id uuid references public.social_media_accounts on delete cascade not null,
  scheduled_time timestamp with time zone not null,
  status text not null default 'pending',
  captions jsonb,
  hashtags jsonb,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create RLS policies
alter table public.users enable row level security;
alter table public.content enable row level security;
alter table public.media enable row level security;
alter table public.analytics enable row level security;
alter table public.social_media_accounts enable row level security;
alter table public.schedules enable row level security;

-- Social media accounts policies
create policy "Users can view social accounts in their projects"
  on public.social_media_accounts for select
  using (
    exists (
      select 1 from public.projects p
      where p.id = social_media_accounts.project_id
      and (
        p.owner_id = auth.uid() 
        or auth.uid() = any(p.allowed_users)
        or p.is_private = false
      )
    )
  );

create policy "Project owners can manage social accounts"
  on public.social_media_accounts for all
  using (
    exists (
      select 1 from public.projects p
      where p.id = social_media_accounts.project_id
      and p.owner_id = auth.uid()
    )
  );

-- Users policies
create policy "Users can view their own data"
  on public.users for select
  using (auth.uid() = id);

create policy "Users can update their own data"
  on public.users for update
  using (auth.uid() = id);

-- Media policies
create policy "Users can view their own media"
  on public.media for select
  using (auth.uid() = user_id);

create policy "Users can upload media"
  on public.media for insert
  with check (auth.uid() = user_id);

create policy "Users can update their own media"
  on public.media for update
  using (auth.uid() = user_id);

create policy "Users can delete their own media"
  on public.media for delete
  using (auth.uid() = user_id);

-- Analytics policies
create policy "Users can view their own analytics"
  on public.analytics for select
  using (exists (
    select 1 from public.content
    where content.id = analytics.content_id
    and content.user_id = auth.uid()
  ));

-- Create functions
create or replace function public.handle_new_user()
returns trigger as $$
begin
  insert into public.users (id, email, full_name)
  values (new.id, new.email, new.raw_user_meta_data->>'full_name');
  return new;
end;
$$ language plpgsql security definer;

-- Create trigger
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();

-- Create maintenance function
CREATE OR REPLACE FUNCTION maintain_ai_tables(
  target_table text,
  target_column text,
  target_value text,
  target_type text
) RETURNS void AS $$
BEGIN
  -- Implementation here
  NULL;
END;
$$ LANGUAGE plpgsql; 