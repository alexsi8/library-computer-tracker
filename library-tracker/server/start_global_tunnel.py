import subprocess
import time
import os
import sys

def check_localtunnel():
    try:
        # Check if localtunnel is installed
        subprocess.run(['lt', '--version'], capture_output=True, text=True, check=True, shell=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_or_run():
    # Since npm isn't globally available, we will try to use Python's built-in urllib to download a standalone pingeo/localtunnel client, 
    # but the simplest zero-dependency way for pure Python is using 'pyngrok' or 'localtunnel' via SSH. 
    # However, 'bore' is a great zero-dependency rust binary. 
    
    # Since we want zero-install, we will use an SSH remote port forwarding to localhost.run, which is built into Windows 10/11 SSH!
    port = 3000
    print(f"Opening secure tunnel for port {port} using localhost.run...")
    print("When the tunnel opens, look for the 'tunneled with tls terminating' URL (e.g., https://xxxxxxxx.localhost.run)")
    print("This URL is your global access link to use on your phone via Cellular data.\n")
    print("Press Ctrl+C to stop.\n")
    
    # Run the SSH tunnel
    # Note: Accept new host keys automatically via StrictHostKeyChecking=no
    ssh_cmd = [
        'ssh', 
        '-R', f'80:localhost:{port}', 
        'nokey@localhost.run', 
        '-o', 'StrictHostKeyChecking=accept-new'
    ]
    
    try:
        process = subprocess.Popen(ssh_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True)
        
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
                # If we see the URL, we can bold it for the user
                if ".localhost.run" in output:
                    print("\n" + "="*60)
                    print(f"🌐 SUCCESS! Your Global Tracker App URL is above!")
                    print("Open that link on your phone (LTE/5G), tap 'Share', and 'Add to Home Screen'")
                    print("="*60 + "\n")
                
    except KeyboardInterrupt:
        print("\nClosing tunnel...")
        process.terminate()
        sys.exit(0)

if __name__ == '__main__':
    install_or_run()
