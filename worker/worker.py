import redis
import psycopg2
import json
import time
import os
import signal
import sys

# Redis connection
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'redis'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    decode_responses=True
)

# PostgreSQL connection
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'postgres'),
        port=int(os.getenv('POSTGRES_PORT', 5432)),
        database=os.getenv('POSTGRES_DB', 'votingdb'),
        user=os.getenv('POSTGRES_USER', 'voting_app'),
        password=os.getenv('POSTGRES_PASSWORD', '')
    )

def init_db():
    """Initialize database tables if not exists"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS votes (
            id SERIAL PRIMARY KEY,
            candidate VARCHAR(50) NOT NULL,
            vote_time TIMESTAMP NOT NULL,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    cur.close()
    conn.close()

def save_vote_to_db(vote_data):
    """Save vote to PostgreSQL"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO votes (candidate, vote_time)
            VALUES (%s, %s)
        """, (vote_data['candidate'], vote_data['timestamp']))
        
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving to DB: {str(e)}")
        return False

def process_votes():
    """Main worker loop - processes votes from Redis queue"""
    print("Worker started. Waiting for votes...")
    
    while True:
        try:
            # Get vote from Redis queue (block for 1 second)
            vote_data = redis_client.blpop('votes_queue', timeout=1)
            
            if vote_data:
                _, vote_json = vote_data
                vote = json.loads(vote_json)
                
                print(f"Processing vote for {vote['candidate']} at {vote['timestamp']}")
                
                # Save to PostgreSQL
                if save_vote_to_db(vote):
                    print(f"✓ Vote saved to database")
                else:
                    print(f"✗ Failed to save vote, requeuing...")
                    # Re-queue failed vote
                    redis_client.rpush('votes_queue', vote_json)
            
            # Small sleep to prevent CPU spinning
            time.sleep(0.1)
            
        except KeyboardInterrupt:
            print("\nWorker shutting down...")
            break
        except Exception as e:
            print(f"Error in worker loop: {str(e)}")
            time.sleep(5)

def signal_handler(sig, frame):
    print('Received shutdown signal')
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    # Initialize database
    init_db()
    
    # Start processing
    process_votes()
