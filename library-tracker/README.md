# Library Computer Availability Tracker

A premium, mobile-responsive web application that tracks the availability of computers in a library in real-time. Built natively with pure Python, Vanilla HTML/CSS/JS, and no external dependencies.

## Architecture
1. **The Server (`server.py`)**: A lightweight Python HTTP server that acts as the central hub. It receives heartbeats and serves the web app frontend.
2. **The Client (`client.py`)**: A smart tracker script installed on each computer. It monitors native Windows OS idle time (mouse/keyboard) to accurately determine if the computer is currently "In-Use" or "Available".
3. **The Web App (`webapp/`)**: A sleek, modern dashboard that fetches real-time updates and dynamically visualizes computer statuses using a glassmorphism design.
4. **Global Tunnel (`start_global_tunnel.py`)**: A zero-dependency SSH tunnel script that securely exposes the local server to the public internet, allowing access from anywhere via cellular data.

## Setup Instructions

### 1. Launch the Central Server
On your main computer, start the server:
```bash
cd server
python server.py
```

### 2. Launch the Tracker Clients
On each library computer to be tracked, run the client with a unique ID:
```bash
cd client
python client.py --id "Library-PC-01" --idle-threshold 300 --interval 15
```
*(300 seconds = 5 minutes of inactivity before marking as "Available")*

### 3. Access the Dashboard locally
Navigate to `http://localhost:3000` on the server computer.

### 4. Global Cellular Access
To use the app on your phone anywhere in the world:
1. Run `python start_global_tunnel.py` in the `server` directory.
2. Open the generated `https://...localhost.run` link on your phone.
3. Tap "Share" -> "Add to Home Screen" to install it as a native app!
