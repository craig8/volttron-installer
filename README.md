# volttron-installer
### Installing Prerequisites
1. Ensure that Python version 3.10[^1] is installed by running `python3.10 --version`
   - If Python 3.10 is not installed, add the deadsnakes PPA by running `sudo add-apt-repository ppa:deadsnakes/ppa`
   - Run `sudo apt update` to refresh the cache
   - Install Python 3.10 by running `sudo apt install python3.10`
   - Validate that Python 3.10 was installed by running `python3.10 --version`
2. Ensure that curl is installed on the system by running `curl --version`
   - If curl is not installed, run `sudo apt install curl` to install it
### Running the Script
1. Run the command `python3 <(curl -sSL https://raw.githubusercontent.com/VOLTTRON/volttron-installer/develop/web.py)`
   - Installs the ansible, git, pexpect, pip and python3.10-venv packages if they are not already installed
   - Creates and activates a virtual environment in the directory where the script was ran
   - Installs the volttron-ansible collection
   - Starts a web server and opens the default browser, pointing to 'http://localhost:8080'
2. Navigating the Web Page
   - Click 'Install Base Requirements' to install what you need for volttron
     - Navigate back to where the script was ran and enter your password to continue the installation process
[^1]: Any version of Python greater than 3.10 will work
