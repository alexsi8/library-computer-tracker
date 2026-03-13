const express = require('express');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

// In-memory store for computer statuses
// Key: machineId (string)
// Value: { status: 'Available' | 'In-Use' | 'Offline', lastHeartbeat: timestamp }
const computers = {};

// Hardcoded timeout (e.g., 2 minutes) for a client to be considered Offline
const OFFLINE_TIMEOUT_MS = 2 * 60 * 1000;

// Helper to check and mark computers offline
const checkOfflineStatus = () => {
  const now = Date.now();
  Object.keys(computers).forEach(id => {
    if (now - computers[id].lastHeartbeat > OFFLINE_TIMEOUT_MS) {
      computers[id].status = 'Offline';
    }
  });
};

// Start a background interval to check for offline computers every minute
setInterval(checkOfflineStatus, 60 * 1000);

// Endpoint to receive heartbeats from the tracker client
app.post('/api/heartbeat', (req, res) => {
  const { machineId, status } = req.body;

  if (!machineId || !status) {
    return res.status(400).json({ error: 'Missing machineId or status' });
  }

  // Update or create the computer record
  computers[machineId] = {
    machineId,
    status,
    lastHeartbeat: Date.now(),
  };

  res.status(200).json({ success: true });
});

// Endpoint for the Web App to fetch all current statuses
app.get('/api/computers', (req, res) => {
  checkOfflineStatus(); // Ensure statuses are up-to-date before sending
  
  // Convert the object into an array for the frontend
  const computersList = Object.values(computers);
  
  res.status(200).json(computersList);
});

// Root endpoint for testing
app.get('/', (req, res) => {
  res.send('Library Tracker Server is running!');
});

app.listen(PORT, () => {
  console.log(`Server listening on port ${PORT}`);
});
