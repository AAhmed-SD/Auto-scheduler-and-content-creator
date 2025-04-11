# Database Setup Documentation

## Table of Contents
1. [Setup Instructions](#setup-instructions)
2. [Migration Procedures](#migration-procedures)
3. [Backup and Restore](#backup-and-restore)
4. [Environment Configurations](#environment-configurations)
5. [Schema Documentation](#schema-documentation)
6. [Data Migration Guide](#data-migration-guide)
7. [Performance Optimization](#performance-optimization)
8. [Security Documentation](#security-documentation)

## Setup Instructions

### Prerequisites
- PostgreSQL 15+
- Supabase CLI
- Node.js 18+ (for migrations)
- Python 3.11+ (for database scripts)

### Installation Steps
1. **Local Development Setup**
   ```bash
   # Install Supabase CLI
   npm install -g supabase

   # Initialize Supabase project
   supabase init

   # Start local Supabase instance
   supabase start
   ```

2. **Database Configuration**
   ```bash
   # Create .env file
   cp .env.example .env

   # Update environment variables
   DATABASE_URL=postgresql://postgres:postgres@localhost:54322/postgres
   SUPABASE_URL=http://localhost:54321
   SUPABASE_ANON_KEY=your-anon-key
   ```

3. **Schema Initialization**
   ```bash
   # Run initial migrations
   supabase db reset
   ```

## Migration Procedures

### Creating Migrations
1. **New Migration**
   ```bash
   supabase migration new <migration_name>
   ```

2. **Migration Structure**
   ```sql
   -- migrate:up
   -- Your SQL for applying the migration
   
   -- migrate:down
   -- Your SQL for rolling back the migration
   ```

### Applying Migrations
```bash
# Apply all pending migrations
supabase db push

# Rollback last migration
supabase db reset
```

## Backup and Restore

### Backup Procedures
1. **Full Database Backup**
   ```bash
   pg_dump -U postgres -d postgres > backup.sql
   ```

2. **Incremental Backup**
   ```bash
   # Using WAL archiving
   archive_command = 'cp %p /path/to/archive/%f'
   ```

### Restore Procedures
1. **Full Restore**
   ```bash
   psql -U postgres -d postgres < backup.sql
   ```

2. **Point-in-Time Recovery**
   ```bash
   # Configure recovery.conf
   restore_command = 'cp /path/to/archive/%f %p'
   recovery_target_time = '2024-01-01 12:00:00'
   ```

## Environment Configurations

### Development
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:54322/postgres
SUPABASE_URL=http://localhost:54321
SUPABASE_ANON_KEY=dev-anon-key
```

### Staging
```env
DATABASE_URL=postgresql://user:pass@staging-db.example.com:5432/dbname
SUPABASE_URL=https://staging-project.supabase.co
SUPABASE_ANON_KEY=staging-anon-key
```

### Production
```env
DATABASE_URL=postgresql://user:pass@prod-db.example.com:5432/dbname
SUPABASE_URL=https://prod-project.supabase.co
SUPABASE_ANON_KEY=prod-anon-key
```

## Schema Documentation

### Table Definitions
```sql
-- Users Table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Projects Table
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    owner_id UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Foreign Key Relationships
```sql
-- Content to Projects
ALTER TABLE content
ADD CONSTRAINT fk_content_project
FOREIGN KEY (project_id) REFERENCES projects(id)
ON DELETE CASCADE;

-- Social Media Posts to Content
ALTER TABLE social_media_posts
ADD CONSTRAINT fk_posts_content
FOREIGN KEY (content_id) REFERENCES content(id)
ON DELETE CASCADE;
```

### Index Definitions
```sql
-- Performance Indexes
CREATE INDEX idx_content_project ON content(project_id);
CREATE INDEX idx_posts_platform ON social_media_posts(platform_id);
CREATE INDEX idx_analytics_content ON content_analytics(content_id);
```

### Constraints
```sql
-- Unique Constraints
ALTER TABLE users ADD CONSTRAINT unique_email UNIQUE (email);
ALTER TABLE projects ADD CONSTRAINT unique_project_name UNIQUE (name, owner_id);

-- Check Constraints
ALTER TABLE content ADD CONSTRAINT valid_status 
CHECK (status IN ('draft', 'scheduled', 'published', 'archived'));
```

### Triggers
```sql
-- Updated At Trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

## Data Migration Guide

### Migration Procedures
1. **Planning**
   - Review current schema
   - Identify data dependencies
   - Create migration strategy

2. **Execution**
   ```bash
   # Create migration
   supabase migration new data_migration

   # Apply migration
   supabase db push
   ```

### Data Validation
```sql
-- Validation Queries
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM projects;
SELECT COUNT(*) FROM content;
```

### Rollback Procedures
```bash
# Rollback last migration
supabase db reset

# Restore from backup
psql -U postgres -d postgres < backup.sql
```

### Testing Procedures
1. **Unit Tests**
   ```bash
   # Run database tests
   pytest tests/database/
   ```

2. **Integration Tests**
   ```bash
   # Run integration tests
   pytest tests/integration/
   ```

## Performance Optimization

### Query Optimization
1. **Indexing Strategy**
   ```sql
   -- Add indexes for frequently queried columns
   CREATE INDEX idx_content_status ON content(status);
   CREATE INDEX idx_posts_scheduled ON social_media_posts(scheduled_time);
   ```

2. **Query Optimization**
   ```sql
   -- Use EXPLAIN ANALYZE
   EXPLAIN ANALYZE SELECT * FROM content WHERE status = 'published';
   ```

### Caching Strategy
1. **Redis Configuration**
   ```env
   REDIS_URL=redis://localhost:6379
   CACHE_TTL=3600
   ```

2. **Cache Implementation**
   ```python
   # Example cache decorator
   @cache(ttl=3600)
   def get_content(content_id):
       return db.query(Content).filter(Content.id == content_id).first()
   ```

### Monitoring
1. **Performance Metrics**
   ```sql
   -- Query performance monitoring
   SELECT * FROM pg_stat_activity;
   SELECT * FROM pg_stat_user_tables;
   ```

2. **Maintenance Tasks**
   ```bash
   # Vacuum analyze
   VACUUM ANALYZE;
   
   # Reindex
   REINDEX TABLE content;
   ```

## Security Documentation

### RLS Policies
```sql
-- Users can only access their own data
CREATE POLICY "Users can view own data"
ON users FOR SELECT
USING (auth.uid() = id);

-- Project members can access project content
CREATE POLICY "Project members can access content"
ON content FOR SELECT
USING (
    project_id IN (
        SELECT project_id FROM project_members
        WHERE user_id = auth.uid()
    )
);
```

### Encryption
1. **Column Encryption**
   ```sql
   -- Encrypt sensitive data
   CREATE EXTENSION IF NOT EXISTS pgcrypto;
   
   ALTER TABLE users
   ADD COLUMN encrypted_data BYTEA;
   ```

2. **Key Management**
   ```env
   ENCRYPTION_KEY=your-encryption-key
   ```

### Access Control Matrix
| Role | Users | Projects | Content | Analytics |
|------|-------|----------|---------|-----------|
| Admin | CRUD | CRUD | CRUD | CRUD |
| Editor | R | R | CRUD | R |
| Viewer | R | R | R | R |

### Audit Logging
```sql
-- Audit table
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_name TEXT NOT NULL,
    operation TEXT NOT NULL,
    user_id UUID REFERENCES users(id),
    old_data JSONB,
    new_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Audit trigger
CREATE OR REPLACE FUNCTION audit_trigger()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_logs (table_name, operation, user_id, new_data)
        VALUES (TG_TABLE_NAME, 'INSERT', auth.uid(), row_to_json(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_logs (table_name, operation, user_id, old_data, new_data)
        VALUES (TG_TABLE_NAME, 'UPDATE', auth.uid(), row_to_json(OLD), row_to_json(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_logs (table_name, operation, user_id, old_data)
        VALUES (TG_TABLE_NAME, 'DELETE', auth.uid(), row_to_json(OLD));
        RETURN OLD;
    END IF;
END;
$$ LANGUAGE plpgsql;
``` 