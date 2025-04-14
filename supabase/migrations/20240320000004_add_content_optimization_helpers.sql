-- Create a function to optimize all draft content for a project
CREATE OR REPLACE FUNCTION public.optimize_project_content(
    p_project_id UUID,
    p_platform VARCHAR DEFAULT NULL
)
RETURNS TABLE (
    content_id UUID,
    title TEXT,
    optimization_suggestions JSONB,
    viral_potential DECIMAL,
    style_alignment DECIMAL,
    recommended_changes JSONB
) AS $$
BEGIN
    RETURN QUERY
    WITH draft_content AS (
        SELECT id, title
        FROM public.content
        WHERE project_id = p_project_id
        AND status = 'draft'
        AND (p_platform IS NULL OR content_type = p_platform)
    )
    SELECT 
        dc.id,
        dc.title,
        opt.optimization_suggestions,
        opt.viral_potential,
        opt.style_alignment,
        opt.recommended_changes
    FROM draft_content dc
    CROSS JOIN LATERAL (
        SELECT * FROM public.optimize_content(dc.id, COALESCE(p_platform, dc.content_type))
    ) opt;
END;
$$ LANGUAGE plpgsql;

-- Example usage:
COMMENT ON FUNCTION public.optimize_project_content IS 
$doc$
Example usage:

-- Optimize all draft content for a project
SELECT * FROM optimize_project_content('your-project-uuid-here');

-- Optimize Instagram content only
SELECT * FROM optimize_project_content('your-project-uuid-here', 'instagram');

-- Get optimization suggestions for specific content
SELECT * FROM optimize_content('your-content-uuid-here', 'instagram');
$doc$;

-- Create a view for easy content optimization analysis
CREATE OR REPLACE VIEW public.content_optimization_summary AS
SELECT 
    c.id as content_id,
    c.title,
    c.project_id,
    c.content_type as platform,
    c.status,
    -- Viral patterns analysis
    vp.pattern_signature,
    vp.success_metrics,
    vp.confidence_score,
    -- Style preferences
    usp.style_profile,
    usp.brand_guidelines,
    -- Optimization rules
    cor.rule_definition,
    cor.success_rate,
    -- Calculate optimization scores
    COALESCE(vp.confidence_score, 0) as viral_confidence,
    COALESCE((cor.success_rate), 0) as optimization_success_rate,
    -- Calculate overall potential
    (
        COALESCE(vp.confidence_score, 0) * 0.4 +
        COALESCE((cor.success_rate), 0) * 0.3 +
        COALESCE((vp.success_metrics->>'engagement_rate')::decimal, 0) * 0.3
    ) as overall_potential_score
FROM 
    public.content c
    LEFT JOIN public.viral_patterns vp 
        ON c.project_id = vp.project_id 
        AND c.content_type = vp.platform
    LEFT JOIN public.user_style_preferences usp 
        ON c.project_id = usp.project_id
    LEFT JOIN public.content_optimization_rules cor 
        ON c.project_id = cor.project_id 
        AND c.content_type = cor.platform
WHERE 
    c.status = 'draft';

-- Create a function to get top performing patterns
CREATE OR REPLACE FUNCTION public.get_top_patterns(
    p_project_id UUID,
    p_platform VARCHAR,
    p_limit INTEGER DEFAULT 5
)
RETURNS TABLE (
    pattern_type TEXT,
    success_rate DECIMAL,
    engagement_rate DECIMAL,
    visual_elements JSONB,
    text_elements JSONB,
    time_factors JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        vp.pattern_signature->>'type' as pattern_type,
        vp.confidence_score as success_rate,
        (vp.success_metrics->>'engagement_rate')::decimal as engagement_rate,
        vp.visual_elements,
        vp.text_elements,
        vp.time_factors
    FROM public.viral_patterns vp
    WHERE 
        vp.project_id = p_project_id
        AND vp.platform = p_platform
        AND vp.confidence_score > 0.5
    ORDER BY 
        vp.confidence_score DESC,
        (vp.success_metrics->>'engagement_rate')::decimal DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- Example usage comments
COMMENT ON VIEW public.content_optimization_summary IS 
$doc$
View for analyzing content optimization potential.

Example usage:
-- Get all draft content optimization summary
SELECT * FROM content_optimization_summary;

-- Get top potential content
SELECT * FROM content_optimization_summary 
WHERE overall_potential_score > 0.7 
ORDER BY overall_potential_score DESC;
$doc$;

COMMENT ON FUNCTION public.get_top_patterns IS 
$doc$
Get top performing content patterns for a project and platform.

Example usage:
-- Get top 5 Instagram patterns
SELECT * FROM get_top_patterns('your-project-uuid-here', 'instagram');

-- Get top 10 TikTok patterns
SELECT * FROM get_top_patterns('your-project-uuid-here', 'tiktok', 10);
$doc$; 