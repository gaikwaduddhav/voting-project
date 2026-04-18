const express = require('express');
const path = require('path');
const axios = require('axios');

const app = express();
const PORT = 3000;
const API_URL = process.env.API_URL || 'http://api:8080';

app.use(express.json());
app.use(express.static('static'));

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

app.get('/api/results', async (req, res) => {
    try {
        const response = await axios.get(`${API_URL}/results`);
        res.json(response.data);
    } catch (error) {
        console.error('Error fetching results:', error.message);
        res.status(500).json({ error: 'Failed to fetch results' });
    }
});

app.post('/api/vote', async (req, res) => {
    try {
        const { candidate } = req.body;
        const response = await axios.post(`${API_URL}/vote`, { candidate });
        res.json(response.data);
    } catch (error) {
        console.error('Error submitting vote:', error.message);
        res.status(500).json({ error: 'Failed to submit vote' });
    }
});

app.get('/health', (req, res) => {
    res.status(200).json({ status: 'healthy', service: 'frontend' });
});

app.listen(PORT, () => {
    console.log(`Frontend running on port ${PORT}`);
});
