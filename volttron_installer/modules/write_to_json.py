import os
import json

# Define the relative path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PERSISTENT_DIR = os.path.join(BASE_DIR, 'persistence_files')

PERSISTENT_HOSTS_FILE = os.path.join(PERSISTENT_DIR, "hosts.json")
PERSISTENT_AGENTS_FILE = os.path.join(PERSISTENT_DIR, "agents.json")
PERSISTENT_DRIVERS_FILE = os.path.join(PERSISTENT_DIR, "drivers.json")

# Ensure the directory exists
os.makedirs(PERSISTENT_DIR, exist_ok=True)

def write_to_file(file: str, global_lst: list) -> None:
    file_map = {
        "hosts" or "h" : PERSISTENT_AGENTS_FILE,
        "agents" or "a": PERSISTENT_AGENTS_FILE,
        "drivers" or "d": PERSISTENT_DRIVERS_FILE,
    }
    with open(file_map[file], "w") as f:
        json.dump(global_lst, f)


def write_to_hosts(data):
    with open(PERSISTENT_HOSTS_FILE, "w") as f:
        json.dump(data, f)

def write_to_agents(data):
    with open(PERSISTENT_AGENTS_FILE, "w") as f:
        json.dump(data, f)



def establish_agents() -> list:
    """Loads agents data from the JSON file and returns it as a list."""
    with open(PERSISTENT_AGENTS_FILE, "r") as f:
        return json.load(f)


def establish_hosts() -> list:
    """Loads hosts data from the JSON file and returns it as a list."""
    with open(PERSISTENT_HOSTS_FILE, "r") as f:
        return json.load(f)

def establish_drivers() -> list:
    with open(PERSISTENT_DRIVERS_FILE, "r") as f:
        return json.load(f)