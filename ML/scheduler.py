# Scheduler that executes the ML CI/CD script every DELAY_TIME seconds
import subprocess
import time
import os

SCRIPT_NAME = "builder.sh"
DELAY_TIME = 30 # In seconds

module_path = os.path.dirname(os.path.abspath(__file__))
script_path = os.path.join(module_path, SCRIPT_NAME)
while(True):
    subprocess.Popen(script_path)
    time.sleep(DELAY_TIME)