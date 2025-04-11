-- Create users table (extends Supabase auth.users)
create table public.users (
  id uuid references auth.users on delete cascade not null primary key,
  email text unique not null,
  full_name text,
  avatar_url text,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create projects table
create table public.projects (
  id uuid default uuid_generate_v4() primary key,
  name text not null,
  description text,
  owner_id uuid references public.users on delete cascade not null,
  is_private boolean default true,
  allowed_users uuid[] default array[]::uuid[],
  settings jsonb default '{}'::jsonb,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Add project policies
create policy "Users can view their own or public projects"
  on public.projects for select
  using (
    owner_id = auth.uid() 
    or auth.uid() = any(allowed_users) 
    or is_private = false
  );

create policy "Users can create projects"
  on public.projects for insert
  with check (auth.uid() = owner_id);

create policy "Project owners can update their projects"
  on public.projects for update
  using (auth.uid() = owner_id);

create policy "Project owners can delete their projects"
  on public.projects for delete
  using (auth.uid() = owner_id);

-- Enable RLS on projects
alter table public.projects enable row level security;

-- Create content table
create table public.content (
  id uuid default uuid_generate_v4() primary key,
  user_id uuid references public.users on delete cascade not null,
  project_id uuid references public.projects on delete cascade not null,
  title text not null,
  description text,
  content_type text not null,
  status text not null default 'draft',
  scheduled_for timestamp with time zone,
  published_at timestamp with time zone,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

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

-- Content policies
create policy "Users can view content in their projects"
  on public.content for select
  using (
    exists (
      select 1 from public.projects p
      where p.id = content.project_id
      and (
        p.owner_id = auth.uid() 
        or auth.uid() = any(p.allowed_users)
        or p.is_private = false
      )
    )
  );

create policy "Users can create content in their projects"
  on public.content for insert
  with check (
    exists (
      select 1 from public.projects p
      where p.id = project_id
      and (p.owner_id = auth.uid() or auth.uid() = any(p.allowed_users))
    )
  );

create policy "Users can update content in their projects"
  on public.content for update
  using (
    exists (
      select 1 from public.projects p
      where p.id = content.project_id
      and (p.owner_id = auth.uid() or auth.uid() = any(p.allowed_users))
    )
  );

create policy "Users can delete content in their projects"
  on public.content for delete
  using (
    exists (
      select 1 from public.projects p
      where p.id = content.project_id
      and (p.owner_id = auth.uid() or auth.uid() = any(p.allowed_users))
    )
  );

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

-- Create storage buckets
insert into storage.buckets (id, name, public)
values ('media', 'media', true);

-- Create storage policies
create policy "Media files are publicly accessible"
  on storage.objects for select
  using (bucket_id = 'media');

create policy "Users can upload media"
  on storage.objects for insert
  with check (bucket_id = 'media' and auth.uid() = owner);

create policy "Users can update their own media"
  on storage.objects for update
  using (bucket_id = 'media' and auth.uid() = owner);

create policy "Users can delete their own media"
  on storage.objects for delete
  using (bucket_id = 'media' and auth.uid() = owner); 