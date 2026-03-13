import json
import time
import urllib.request
import argparse
import ctypes
import os

# Server Configuration
SERVER_URL = "http://localhost:3000/api/heartbeat"

class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", ctypes.c_uint),
        ("dwTime", ctypes.c_int) # OS tick count for last input
    ]

def get_idle_time_seconds():
    """Returns the system idle time in seconds, specifically for Windows."""
    if os.name == 'nt':
        last_input_info = LASTINPUTINFO()
        last_input_info.cbSize = ctypes.sizeof(last_input_info)
        if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(last_input_info)):
            millis = ctypes.windll.kernel32.GetTickCount() - last_input_info.dwTime
            return millis / 1000.0
    # Fallback if not Windows or failure
    return 0

def send_heartbeat(machine_id, status):
    data = json.dumps({
        "machineId": machine_id,
        "status": status
    }).encode("utf-8")
    
    req = urllib.request.Request(SERVER_URL, data=data, headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req)
        print(f"[{time.strftime('%H:%M:%S')}] Heartbeat sent: {machine_id} -> {status}")
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] Failed to send heartbeat: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Library Computer Tracker Client")
    parser.add_argument("--id", type=str, required=True, help="Unique Machine ID (e.g., PC-01)")
    parser.add_argument("--idle-threshold", type=int, default=60, help="Seconds of idle time before marking as Available")
    parser.add_argument("--interval", type=int, default=15, help="Heartbeat interval in seconds")
    
    args = parser.parse_args()
    
    print(f"Starting Tracker for {args.id}...")
    print(f"Idle Threshold: {args.idle_threshold}s | Interval: {args.interval}s")
    
    while True:
        idle_time = get_idle_time_seconds()
        
        if idle_time > args.idle_threshold:
            status = "Available"
        else:
            status = "In-Use"
            
        send_heartbeat(args.id, status)
        time.sleep(args.interval)
