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

def establish_agents() -> list:
    """
    Loads hosts data from the JSON file and returns it as a list.

    Args:
        None

    Returns:
        A list of host dictionaries loaded from the JSON file.
    """
    with open(PERSISTENT_AGENTS_FILE, "r") as f:
        return json.load(f)


def establish_hosts() -> list:
    """
    Loads hosts data from the JSON file and returns it as a list.

    Args:
        None

    Returns:
        A list of host dictionaries loaded from the JSON file.
    """
    with open(PERSISTENT_HOSTS_FILE, "r") as f:
        return json.load(f)
