const express = require('express');
const app = express();
const PORT = 3000;

app.use(express.json());
app.use(express.static('.'));

app.get('/', (req, res) => {
    res.send(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Voting App</title>
            <style>
                body { font-family: Arial; text-align: center; padding: 50px; }
                button { margin: 10px; padding: 15px 30px; font-size: 18px; }
            </style>
        </head>
        <body>
            <h1>🗳️ Voting App</h1>
            <div>
                <button onclick="vote('candidate_a')">🐱 Candidate A</button>
                <button onclick="vote('candidate_b')">🐶 Candidate B</button>
                <button onclick="vote('candidate_c')">🦊 Candidate C</button>
            </div>
            <div id="results" style="margin-top: 30px;"></div>
            <script>
                async function vote(candidate) {
                    const response = await fetch('/api/vote', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({candidate})
                    });
                    const data = await response.json();
                    alert('Voted for ' + candidate);
                    loadResults();
                }
                
                async function loadResults() {
                    const response = await fetch('/api/results');
                    const data = await response.json();
                    document.getElementById('results').innerHTML = 
                        '<h3>Results</h3>' +
                        '<p>Candidate A: ' + (data.candidate_a || 0) + '</p>' +
                        '<p>Candidate B: ' + (data.candidate_b || 0) + '</p>' +
                        '<p>Candidate C: ' + (data.candidate_c || 0) + '</p>';
                }
                
                loadResults();
                setInterval(loadResults, 3000);
            </script>
        </body>
        </html>
    `);
});

app.get('/health', (req, res) => {
    res.json({ status: 'healthy', service: 'frontend' });
});

app.listen(PORT, () => {
    console.log(`Frontend running on http://localhost:${PORT}`);
});
