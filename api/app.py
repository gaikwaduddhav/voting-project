from flask import Flask, request, jsonify
import redis
import os
import json
from datetime import datetime
import hashlib

app = Flask(__name__)

# Redis connection
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'redis'),
    port=6379,
    decode_responses=True
)

def get_voter_key(voter_id):
    """Create a unique key for voter"""
    return f"voter:{voter_id}"

def has_voter_voted(voter_id):
    """Check if this voter has already voted"""
    return redis_client.exists(get_voter_key(voter_id))

def record_voter(voter_id, candidate):
    """Record that this voter has voted"""
    redis_client.setex(
        get_voter_key(voter_id),
        86400 * 30,  # Store for 30 days
        json.dumps({'candidate': candidate, 'timestamp': datetime.now().isoformat()})
    )

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/vote', methods=['POST'])
def vote():
    try:
        data = request.get_json()
        candidate = data.get('candidate')
        voter_id = data.get('voter_id')
        
        # Validate candidate
        if not candidate or candidate not in ['candidate_a', 'candidate_b', 'candidate_c']:
            return jsonify({'error': 'Invalid candidate'}), 400
        
        # Check if voter exists
        if not voter_id:
            return jsonify({'error': 'Missing voter identification'}), 400
        
        # Check if already voted
        if has_voter_voted(voter_id):
            return jsonify({'error': 'You have already voted! Only one vote per device is allowed.'}), 403
        
        # Record vote in Redis queue
        redis_client.rpush('votes_queue', json.dumps({
            'candidate': candidate,
            'voter_id': voter_id,
            'timestamp': datetime.now().isoformat()
        }))
        
        # Increment vote count in Redis cache
        redis_client.hincrby('vote_counts', candidate, 1)
        
        # Mark voter as voted
        record_voter(voter_id, candidate)
        
        return jsonify({
            'message': f'Vote for {candidate} recorded successfully',
            'candidate': candidate
        }), 200
    
    except Exception as e:
        app.logger.error(f'Error processing vote: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/results', methods=['GET'])
def results():
    try:
        vote_counts = redis_client.hgetall('vote_counts')
        
        results = {
            'candidate_a': int(vote_counts.get('candidate_a', 0)),
            'candidate_b': int(vote_counts.get('candidate_b', 0)),
            'candidate_c': int(vote_counts.get('candidate_c', 0))
        }
        
        # Get total unique voters
        total_voters = len(redis_client.keys('voter:*'))
        
        return jsonify({
            **results,
            'total_voters': total_voters
        }), 200
    
    except Exception as e:
        app.logger.error(f'Error fetching results: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/stats', methods=['GET'])
def stats():
    """Get voting statistics"""
    try:
        total_voters = len(redis_client.keys('voter:*'))
        queue_size = redis_client.llen('votes_queue')
        
        return jsonify({
            'total_votes_cast': total_voters,
            'pending_votes': queue_size,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
