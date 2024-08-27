import os
import json

# Define the relative path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PERSISTENT_DIR = os.path.join(BASE_DIR, 'persistence_files')

PERSISTENT_HOSTS_FILE = os.path.join(PERSISTENT_DIR, "hosts.json")
PERSISTENT_AGENTS_FILE = os.path.join(PERSISTENT_DIR, "agents.json")
PERSISTENT_DRIVERS_FILE = os.path.join(PERSISTENT_DIR, "drivers.json")
PERSISTENT_PLATFORM_ID_FILE = os.path.join(PERSISTENT_DIR, "tile_id.json")

# Ensure the directory exists
os.makedirs(PERSISTENT_DIR, exist_ok=True)

file_map = {
    "hosts" or "h" : PERSISTENT_HOSTS_FILE,
    "agents" or "a": PERSISTENT_AGENTS_FILE,
    "drivers" or "d": PERSISTENT_DRIVERS_FILE,
    "tile_id" or "pID": PERSISTENT_PLATFORM_ID_FILE,
}

def write_to_file(file: str, var: any) -> None:
    """
    Takes a variable, typically a `list`, then dumps that into a persistent
    JSON file that the app will read and right from.

    list of file names:
    hosts, agents, drivers, platform_id
    """
    with open(file_map[file], "w") as f:
        json.dump(var, f)

def dump_to_var(file: str) -> any:
    """Takes file name and returns corresponding JSON dump"""
    with open(file_map[file], "r") as f:
        return json.load(f)