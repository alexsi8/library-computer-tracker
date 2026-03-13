import json
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import os

# In-memory store for computer statuses
# Key: machineId (str)
# Value: { status: 'Available' | 'In-Use' | 'Offline', lastHeartbeat: timestamp }
computers = {}

# Offline timeout (e.g., 2 minutes)
OFFLINE_TIMEOUT_MS = 2 * 60 * 1000

def check_offline_status():
    now = time.time() * 1000
    for id, info in computers.items():
        if (now - info['lastHeartbeat']) > OFFLINE_TIMEOUT_MS:
            info['status'] = 'Offline'

class TrackerHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/api/heartbeat':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                machine_id = data.get('machineId')
                status = data.get('status')
                
                if not machine_id or not status:
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(b'{"error": "Missing machineId or status"}')
                    return
                
                computers[machine_id] = {
                    'machineId': machine_id,
                    'status': status,
                    'lastHeartbeat': time.time() * 1000
                }
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"success": true}')
                print(f"[{machine_id}] Status updated to: {status}")
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        # API Route logic
        if parsed_path.path == '/api/computers':
            check_offline_status()
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(list(computers.values())).encode('utf-8'))
        else:
            # Simple static file server serving the webapp folder
            # Redirect root to index.html
            if self.path == '/':
                self.path = '/index.html'
            super().do_GET()

def start_offline_checker():
    while True:
        check_offline_status()
        time.sleep(60)

if __name__ == '__main__':
    PORT = 3000
    # Change current working directory to the webapp so static files serve correctly
    webapp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'webapp')
    if not os.path.exists(webapp_dir):
        os.makedirs(webapp_dir)
    os.chdir(webapp_dir)

    server_address = ('', PORT)
    httpd = HTTPServer(server_address, TrackerHandler)
    
    # Start background thread for offline checks
    checker_thread = threading.Thread(target=start_offline_checker, daemon=True)
    checker_thread.start()
    
    print(f"Library Tracker Server running on port {PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print("Server stopped.")
