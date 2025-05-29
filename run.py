import os
import subprocess
import sys
import time

BACKEND_DIR = os.path.join(os.path.dirname(__file__), 'backend')
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), 'frontend')

print("[1/2] Starting backend server with Hypercorn...")
backend_cmd = [sys.executable, '-m', 'hypercorn', 'main:app', '--reload']

try:
    subprocess.Popen(backend_cmd, cwd=BACKEND_DIR)
    print("Backend server started at http://localhost:8000")
except Exception as e:
    print(f"Failed to start backend: {e}")
    sys.exit(1)

print("[2/2] To start the frontend, open a new terminal and run:")
print(f"    cd {FRONTEND_DIR}")
print("    npm install (if not already done)")
print("    npm start")
print("Frontend will be available at http://localhost:3000\n")

print("You can now open http://localhost:3000 in your browser.")

# Optionally, wait and keep the script running
try:
    while True:
        time.sleep(60)
except KeyboardInterrupt:
    print("\nShutting down run.py script.") 