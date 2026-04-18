-- Create extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create votes table
CREATE TABLE IF NOT EXISTS votes (
    id SERIAL PRIMARY KEY,
    candidate VARCHAR(50) NOT NULL,
    vote_time TIMESTAMP NOT NULL,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_votes_candidate ON votes(candidate);
CREATE INDEX IF NOT EXISTS idx_votes_time ON votes(vote_time);

-- Create view for real-time results
CREATE OR REPLACE VIEW vote_results AS
SELECT 
    candidate,
    COUNT(*) as vote_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 2) as percentage
FROM votes
GROUP BY candidate
ORDER BY vote_count DESC;

-- Create function to get vote counts
CREATE OR REPLACE FUNCTION get_vote_counts()
RETURNS TABLE(candidate TEXT, vote_count BIGINT) AS $$
BEGIN
    RETURN QUERY
    SELECT v.candidate, COUNT(*) as vote_count
    FROM votes v
    GROUP BY v.candidate;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO voting_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO voting_app;
