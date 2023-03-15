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

# Check if the ansible package is installed; Install ansible if not installed
print("Now checking if the ansible package is installed.")
dpkg_output = subprocess.check_output(['dpkg', '-l'])

packages = [line.split()[1] for line in dpkg_output.decode().splitlines() if line.startswith('ii')]
for package in packages:
    if package == "ansible":
        ansible_installed = True
        break
    else:
        ansible_installed = False
    
if not ansible_installed:
    print("Ansible has not been installed. Now installing the ansible package using apt.")
    Popen(['bash', '-c', 'sudo apt install ansible']).wait()
    print("Ansible has now been installed.")
elif ansible_installed:
    print("Ansible is already installed")

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
        print("Now overriding the current virtual environment.")
        Popen(['bash', '-c', 'python3 -m venv .venv']).wait()
        print("The virtual environment '.venv' has been created and has overridden the previous virtual environment.")

