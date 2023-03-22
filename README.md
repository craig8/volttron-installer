# volttron-installer
<<<<<<< HEAD
### Installing Prerequisites
1. Ensure that Python version 3.10[^1] is installed by running `python3.10 --version`
   - If Python 3.10 is not installed, add the deadsnakes PPA by running `sudo add-apt-repository ppa:deadsnakes/ppa`
   - Run `sudo apt update` to refresh the cache
   - Install Python 3.10 by running `sudo apt install python3.10`
   - Validate that Python 3.10 was installed by running `python3.10 --version`
2. Ensure that curl is installed on the system by running `curl --version`
   - If curl is not installed, run `sudo apt install curl` to install it
### Running the Script
1. Run the command `curl -sSL https://github.com/VOLTTRON/volttron-installer/blob/main/web.py | python3 -`
   - Installs the ansible and git packages if they are not already installed
   - Creates and activates a virtual environment in the directory where the script was ran
   - Installs the volttron-ansible package
   - Starts a web server and opens the default browser, pointing to 'http://localhost:8080'

[^1]: Any version of Python greater than 3.10 will work
=======
>>>>>>> 7963aec (Update README.md)
