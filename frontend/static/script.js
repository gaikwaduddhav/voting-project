// Use sessionStorage instead of localStorage (clears when browser closes)
let hasVoted = sessionStorage.getItem('hasVoted');

async function fetchResults() {
    try {
        const response = await fetch('/api/results');
        const data = await response.json();
        
        document.getElementById('votes-a').textContent = data.candidate_a || 0;
        document.getElementById('votes-b').textContent = data.candidate_b || 0;
        document.getElementById('votes-c').textContent = data.candidate_c || 0;
        
        const total = (data.candidate_a || 0) + (data.candidate_b || 0) + (data.candidate_c || 0);
        document.getElementById('total-votes').textContent = `Total Votes: ${total}`;
        
        if (total > 0) {
            document.getElementById('progress-a').style.width = `${((data.candidate_a || 0) / total) * 100}%`;
            document.getElementById('progress-a').textContent = `${Math.round(((data.candidate_a || 0) / total) * 100)}%`;
            
            document.getElementById('progress-b').style.width = `${((data.candidate_b || 0) / total) * 100}%`;
            document.getElementById('progress-b').textContent = `${Math.round(((data.candidate_b || 0) / total) * 100)}%`;
            
            document.getElementById('progress-c').style.width = `${((data.candidate_c || 0) / total) * 100}%`;
            document.getElementById('progress-c').textContent = `${Math.round(((data.candidate_c || 0) / total) * 100)}%`;
        }
    } catch (error) {
        console.error('Error fetching results:', error);
    }
}

async function submitVote(candidate) {
    // Check session storage for vote
    if (sessionStorage.getItem('hasVoted') === 'true') {
        alert('You have already voted in this session!');
        return;
    }
    
    const buttons = document.querySelectorAll('.candidate-btn');
    buttons.forEach(btn => btn.disabled = true);
    
    try {
        // Generate session-based voter ID
        const voterId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        
        const response = await fetch('/api/vote', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                candidate: candidate,
                voter_id: voterId
            }),
        });
        
        const data = await response.json();
        
        if (response.ok) {
            sessionStorage.setItem('hasVoted', 'true');
            alert(`✓ Vote cast for ${candidate.replace('_', ' ')}!`);
            location.reload(); // Reload to show results
        } else {
            alert(`✗ Error: ${data.error}`);
            buttons.forEach(btn => btn.disabled = false);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Network error. Please try again.');
        buttons.forEach(btn => btn.disabled = false);
    }
}

// Check if already voted in this session
if (sessionStorage.getItem('hasVoted') === 'true') {
    document.getElementById('voting-section').style.display = 'none';
    document.getElementById('results-section').style.display = 'block';
    fetchResults();
    setInterval(fetchResults, 3000);
}
