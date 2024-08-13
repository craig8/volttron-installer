import os
import json

# Define the relative path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PERSISTENT_DIR = os.path.join(BASE_DIR, 'persistence_files')

PERSISTENT_HOSTS_FILE = os.path.join(PERSISTENT_DIR, "hosts.json")
PERSISTENT_AGENTS_FILE = os.path.join(PERSISTENT_DIR, "agents.json")

# Ensure the directory exists
os.makedirs(PERSISTENT_DIR, exist_ok=True)

def write_to_hosts(data):
    with open(PERSISTENT_HOSTS_FILE, "w") as f:
        json.dump(data, f)

def write_to_agents(data):
    with open(PERSISTENT_AGENTS_FILE, "w") as f:
        json.dump(data, f)