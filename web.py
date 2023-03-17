from subprocess import Popen, run, call, check_output
import subprocess
import sys
import os
import time

# Check python version. If less than 3.10; Install latest version of python if not installed or correct version
if sys.version_info < (3, 10):
    print("You do not have version Python version 3.10 or higher installed. Now installing the latest version with apt.")
    Popen(['bash', '-c', 'sudo apt install python3 python3-venv']).wait()
    print("The lastest version of Python 3 has been installed.")

# Check if the ansible and git package are installed; Install ansible and git if not installed
print("Now checking if the ansible package is installed.")
dpkg_output = subprocess.check_output(['dpkg', '-l'])

packages = [line.split()[1] for line in dpkg_output.decode().splitlines() if line.startswith('ii')]
for package in packages:
    if package == "ansible":
        ansible_installed = True
        break
    else:
        ansible_installed = False

    if package == "git":
        git_installed = True
        break
    else:
        git_installed =False
    
if not ansible_installed:
    print("Ansible has not been installed. Now installing the ansible package using apt.")
    Popen(['bash', '-c', 'sudo apt install ansible']).wait()
    print("Ansible has now been installed.")
elif ansible_installed:
    print("Ansible is already installed.")

if not git_installed:
    print("Git has not been installed. Now installing the git package using apt.")
    Popen(['bash', '-c', 'sudo apt install git']).wait()
    print("Git has now been installed.")
elif git_installed:
    print("Git is already installed.")

'''
    Checks whether a virtual environment under .venv exists in the current directory; 
    If not, create a virtual environment under the current directory as .venv;
    If there is a virtual environment under .venv, ask the user if they want to 
    override the current .venv or name the virtual environment as something else.
'''
print("Now checking if the virtual environment '.venv' exists")
if not os.path.exists('.venv'):
    print("The virtual environment '.venv' does not exist. Now creating the virtual environment as .venv")
    Popen(['bash', '-c', 'python3 -m venv .venv']).wait()
    print("The virtual environment '.venv' has been created")
elif os.path.exists('.venv'):
    override = str(input("The virtual environment '.venv' does exist. Would you like to override it? (yes or no) "))
    if (override == "y" or override == "Y" or 
        override == "yes" or override == "Yes" or 
        override == "yEs" or override == "yeS" or
        override == "YEs" or override == "YeS" or
        override == "yES" or override == "YES" ):
        override = True
        venv_name = False
        print("Now overriding the current virtual environment.")
        Popen(['bash', '-c', 'python3 -m venv .venv']).wait()
        print("The virtual environment '.venv' has been created and has overridden the previous virtual environment.")
    elif (override == "n" or override == "N" or
          override == "no" or override == "No" or
          override == "nO" or override == "NO"):
          override = False
          venv_name = str(input("What would you like the new virtual environment to be named? "))
          print(f"Now creating the virtual environment '{venv_name}'.")
          Popen(['bash', '-c', f'python3 -m venv {venv_name}']).wait()
          print(f"The virtual environment '{venv_name}' has been created.")

# Activate the virtual environment and install volttron-ansible depending on whether the venv was overriden or not.
if override:
    print("Now activating the virtual environment '.venv' and installing the volttron-ansible package.")
    Popen(['bash', '-c', 'source .venv/bin/activate && ansible-galaxy install git+https://github.com/volttron/volttron-ansible.git']).wait()
    print("The volttron-ansible package has been installed inside the virtual environment '.venv.'")
if not override:
    print(f"Now activating the virtual environemnt '{venv_name}' and installing the volttron-ansible package.")
    Popen(['bash', '-c', f'source {venv_name}/bin/activate && ansible-galaxy install git+https://github.com/volttron/volttron-ansible.git']).wait()
    print(f"The volttron-ansible package has been installed inside the virtual environment '{venv_name}'.")
