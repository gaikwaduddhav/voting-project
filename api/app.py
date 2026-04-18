from flask import Flask, request, jsonify
import redis
import psycopg2
import os
import json
from datetime import datetime

app = Flask(__name__)

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

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/vote', methods=['POST'])
def vote():
    try:
        data = request.get_json()
        candidate = data.get('candidate')
        
        if not candidate or candidate not in ['candidate_a', 'candidate_b', 'candidate_c']:
            return jsonify({'error': 'Invalid candidate'}), 400
        
        # Store vote in Redis (temporary queue)
        redis_client.rpush('votes_queue', json.dumps({
            'candidate': candidate,
            'timestamp': datetime.now().isoformat()
        }))
        
        # Increment vote count in Redis cache
        redis_client.hincrby('vote_counts', candidate, 1)
        
        return jsonify({'message': f'Vote for {candidate} recorded', 'candidate': candidate}), 200
    
    except Exception as e:
        app.logger.error(f'Error processing vote: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/results', methods=['GET'])
def results():
    try:
        # Get vote counts from Redis cache
        vote_counts = redis_client.hgetall('vote_counts')
        
        results = {
            'candidate_a': int(vote_counts.get('candidate_a', 0)),
            'candidate_b': int(vote_counts.get('candidate_b', 0)),
            'candidate_c': int(vote_counts.get('candidate_c', 0))
        }
        
        return jsonify(results), 200
    
    except Exception as e:
        app.logger.error(f'Error fetching results: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
