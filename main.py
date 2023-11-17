from subprocess import Popen, PIPE, check_output, check_call

import os
import time
import sys

# Variables for package installation
ansible_installed = False
git_installed = False
nicegui_installed = False
pip_installed = False
pexpect_installed = False
pexpect_upgraded = False
venv_installed = False
INSTALLER_VENV = ".venv_installer"
requirements = ["ansible", "nicegui", "pexpect>=4"]


if INSTALLER_VENV not in sys.prefix:
    # Check python version. If not 3.10, prompt user to download Python 3.10 and exit program
    python_version_cmd = Popen(["bash", "-c", "python3.10 -V"], stdout=PIPE, stderr=PIPE)
    python_version = python_version_cmd.stdout.read().decode("utf-8")
    if not python_version.startswith("Python 3.10"):
        print("Python 3.10 has not been installed. Please install Python 3.10 before continuing.")
        print("Exiting...")
        sys.exit(1)

    if not sys.version_info >= (3, 10):
        print(f"Python 3.10 is installed, but not the current version being used {sys.executable}.")
        sys.exit(1)
    
    # Check if the required packages are installed; Install the packages if uninstalled
    print("Checking if the required packages are installed.")
    # time.sleep(0.5)

    dpkg_output = check_output(["dpkg", "-l"])
    packages = [line.split()[1] for line in dpkg_output.decode().splitlines() if line.startswith("ii")]
    if "python3.10-venv" not in packages:
        print("Python3.10-venv has not been installed. Now installing the python3.10-venv package using apt.")
        Popen(["bash", "-c", "sudo apt-get install -y python3.10-venv"]).wait()
        print("Python3.10-venv has now been installed.")


# We know we are using the right env if it is in the prefix.
if INSTALLER_VENV not in sys.prefix:
    if not os.path.exists(INSTALLER_VENV):
        result = check_call([sys.executable, "-m", "venv", INSTALLER_VENV])
        if result != 0:
            print("Error creating virtual environment for installer")
            sys.exit(result)
    env = os.environ.copy()
    env['PATH'] = f"{os.path.abspath(INSTALLER_VENV)}/bin:{env['PATH']}"
    result = check_call([f"{INSTALLER_VENV}/bin/python", sys.argv[0]], env=env)
    sys.exit(result)

# Check if the required packages are installed; Install the packages if not installed
output = check_output([sys.executable, "-m", "pip", "freeze"], text=True).splitlines()

for rq in requirements:
    try:
        if ">=" in rq:
            rq = rq.split(">=")[0]
        elif "==" in rq:
            rq = rq.split("==")[0]
        found = next(filter(lambda x: x.startswith(rq), output))
    except StopIteration:
        print(f"Installing {rq}")
        result = check_call([sys.executable, "-m", "pip", "install", rq])
        if result != 0:
            print(f"Error installing {rq}")
            sys.exit(result)

if not os.path.exists(os.path.expanduser("~/.ansible/collections/ansible_collections/volttron")):
    result = check_call(["ansible-galaxy", "collection", "install", "git+https://github.com/VOLTTRON/volttron-ansible.git,develop"])

if not os.path.exists("volttron-installer"):
    Popen(["bash", "-c", "git clone --branch virtualenv https://github.com/craig8/volttron-installer.git", "volttron-installer"]).wait()

# Start NiceGUI
Popen([sys.executable, "volttron-installer/pages.py"]).wait()
