-- Unified Supabase Schema for Algarve É Um System

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table: published_content
-- Stores curated news articles selected by the Orchestrator
CREATE TABLE published_content (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    url TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    summary TEXT,
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'published')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc', now()),
    approved_at TIMESTAMP WITH TIME ZONE
);

-- Table: generated_posts
-- Stores AI-generated content linked to published_content
CREATE TABLE generated_posts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_id UUID REFERENCES published_content(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL CHECK (platform IN ('instagram_post', 'instagram_story', 'facebook_post')),
    caption TEXT,
    story_text TEXT,
    score INTEGER CHECK (score >= 0 AND score <= 100),
    improvement_suggestions JSONB, -- Stored as a JSON array of strings
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc', now())
);

-- Table: calendar_entries
-- Stores planned content for the 30-day calendar
CREATE TABLE calendar_entries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    date TIMESTAMP WITH TIME ZONE NOT NULL,
    content_type VARCHAR(100) NOT NULL,
    topic TEXT NOT NULL,
    platform VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'planned' CHECK (status IN ('planned', 'drafted', 'scheduled', 'published')),
    post_id UUID REFERENCES generated_posts(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc', now())
);

-- Table: analytics
-- Stores performance metrics for published posts
CREATE TABLE analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    post_id UUID REFERENCES generated_posts(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,
    likes INTEGER DEFAULT 0,
    reach INTEGER DEFAULT 0,
    saves INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    engagement_rate NUMERIC(5,2) DEFAULT 0.00,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc', now())
);

-- Table: hashtag_performance
-- Tracks the performance of various hashtags used across posts
CREATE TABLE hashtag_performance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    hashtag VARCHAR(100) UNIQUE NOT NULL,
    uses INTEGER DEFAULT 0,
    avg_engagement NUMERIC(5,2) DEFAULT 0.00,
    last_used TIMESTAMP WITH TIME ZONE
);

-- Basic Row Level Security (RLS) policies for external clients (optional depending on API usage)
-- In a backend service environment using a service role key, RLS can usually be bypassed, 
-- but it's good practice to enable it if exposing directly via client keys.

ALTER TABLE published_content ENABLE ROW LEVEL SECURITY;
ALTER TABLE generated_posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE calendar_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE analytics ENABLE ROW LEVEL SECURITY;
ALTER TABLE hashtag_performance ENABLE ROW LEVEL SECURITY;

-- Note: In Supabase, if your python script uses the SUPABASE_SERVICE_ROLE_KEY, it will bypass RLS.
-- If using ANON key, you need to define permissive or restrictive policies here.
-- Example permissive policy (For testing):
-- CREATE POLICY "Allow all operations for service role" ON published_content USING (true) WITH CHECK (true);
