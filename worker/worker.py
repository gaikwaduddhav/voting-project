import redis
import psycopg2
import json
import time
import os

print("Secure Worker starting...")

# Redis connection
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'redis'),
    port=6379,
    decode_responses=True
)

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'postgres'),
        port=5432,
        database='votingdb',
        user='voting_app',
        password='password'
    )

def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Create votes table with voter tracking
        cur.execute("""
            CREATE TABLE IF NOT EXISTS votes (
                id SERIAL PRIMARY KEY,
                candidate VARCHAR(50) NOT NULL,
                voter_id VARCHAR(255) NOT NULL UNIQUE,
                vote_time TIMESTAMP NOT NULL,
                ip_address VARCHAR(45),
                user_agent TEXT
            )
        """)
        
        # Create index for faster lookups
        cur.execute("CREATE INDEX IF NOT EXISTS idx_voter_id ON votes(voter_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_vote_time ON votes(vote_time)")
        
        conn.commit()
        cur.close()
        conn.close()
        print("✓ Database initialized with voter tracking")
    except Exception as e:
        print(f"Database init error: {e}")

def save_vote_to_db(vote):
    """Save vote to PostgreSQL with voter tracking"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO votes (candidate, voter_id, vote_time)
            VALUES (%s, %s, %s)
            ON CONFLICT (voter_id) DO NOTHING
        """, (vote['candidate'], vote['voter_id'], vote['timestamp']))
        
        conn.commit()
        affected = cur.rowcount
        cur.close()
        conn.close()
        
        return affected > 0
    except Exception as e:
        print(f"Error saving to DB: {e}")
        return False

def process_votes():
    print("Worker is running. Waiting for votes...")
    
    while True:
        try:
            vote_data = redis_client.blpop('votes_queue', timeout=1)
            
            if vote_data:
                _, vote_json = vote_data
                vote = json.loads(vote_json)
                print(f"Processing vote from voter: {vote['voter_id'][:20]}... for {vote['candidate']}")
                
                if save_vote_to_db(vote):
                    print(f"✓ Vote saved to database")
                else:
                    print(f"✗ Failed to save vote (possible duplicate)")
                    # Don't re-queue to prevent duplicate processing
            
            time.sleep(0.1)
            
        except KeyboardInterrupt:
            print("\nWorker shutting down...")
            break
        except Exception as e:
            print(f"Worker error: {e}")
            time.sleep(5)

if __name__ == '__main__':
    init_db()
    process_votes()
