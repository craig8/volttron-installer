from subprocess import Popen, run, call, check_output, PIPE
from http.server import BaseHTTPRequestHandler, HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import parse_qs
import webbrowser
import json
import sys
import os
import time

# Varibales for package installation
pip_installed = False
ansible_installed = False
git_installed = False
venv_installed = False
pexpect_installed = False
pexpect_upgraded = False

# Check python version. If not 3.10, prompt user to download Python 3.10 and exit program
python_version_cmd = Popen(['bash', '-c', 'python3.10 -V'], stdout=PIPE, stderr=PIPE)
python_version = python_version_cmd.stdout.read().decode("utf-8")

if not python_version.startswith("Python 3.10"):
    print("Python 3.10 has not been installed. Please install Python 3.10 before continuing.")
    print("Exiting...")
    sys.exit(1)

# Check if the ansible, git, pexpect, pip and python3.10-venv packages are installed; Install ansible, git, pexpect, pip and python3.10-venv if not installed
print("Now checking if the ansible, git, pexpect, pip and python3.10-venv packages are installed.")
time.sleep(1)

dpkg_output = check_output(['dpkg', '-l'])
packages = [line.split()[1] for line in dpkg_output.decode().splitlines() if line.startswith('ii')]

pexpect_version_cmd = Popen(['bash', '-c', 'pip freeze | grep pexpect'], stdout=PIPE, stderr=PIPE)
pexpect_version = pexpect_version_cmd.stdout.read().decode("utf-8")

for package in packages:
    if package == "ansible":
        ansible_installed = True
    if package == "git":
        git_installed = True
    if package == "python3-pip":
        pip_installed = True
    if package == "python3.10-venv":
        venv_installed = True

if pexpect_version.startswith("pexpect==4"):
    pexpect_installed = True
    pexpect_upgraded = True
elif not pexpect_version.startswith("pexpect==4"):
    pexpect_installed = True
    pexpect_upgraded = False

if not ansible_installed:
    print("Ansible has not been installed. Now installing the ansible package using apt.")
    Popen(['bash', '-c', 'sudo apt-get install -y ansible']).wait()
    print("Ansible has now been installed.")
elif ansible_installed:
    print("Ansible is already installed.")

if not git_installed:
    print("Git has not been installed. Now installing the git package using apt.")
    Popen(['bash', '-c', 'sudo apt-get install -y git']).wait()
    print("Git has now been installed.")
elif git_installed:
    print("Git is already installed.")

if not pip_installed:
    print("Pip has not been installed. Now installing the pip package using apt.")
    Popen(['bash', '-c', 'sudo apt install python3-pip']).wait()
    print("Pip has now been installed.")
elif pip_installed:
    print("Pip is already installed.")

if not pexpect_installed:
    print("Pexpect has not been installed. Now installing the pexpect package.")
    Popen(['bash', '-c', 'pip install pexpect']).wait()
    print("Pexpect has been installed to its latest version.")
elif pexpect_installed and not pexpect_upgraded:
    print("Pexpect is installed but is not the correct version. Now updating the pexpect package.")
    Popen(['bash', '-c', 'pip install --upgrade pexpect']).wait()
    print("Pexpect has been upgraded to its latest version.")
elif pexpect_installed and pexpect_upgraded:
    print("Pexpect has already been installed")

if not venv_installed:
    print("Python3.10-venv has not been installed. Now installing the python3.10-venv package using apt.")
    Popen(['bash', '-c', 'sudo apt-get install -y python3.10-venv']).wait()
    print("Python3.10-venv has now been installed.")
elif venv_installed:
    print("Python3.10-venv is already installed.")

'''
    Checks whether a virtual environment under .venv exists in the current directory; 
    If not, create a virtual environment under the current directory as .venv;
    If there is a virtual environment under .venv, ask the user if they want to 
    override the current .venv or name the virtual environment as something else.
'''
print("Now checking if the virtual environment '.venv' exists.")
time.sleep(1)
if not os.path.exists('.venv'):
    print("The virtual environment '.venv' does not exist. Now creating the virtual environment as .venv")
    Popen(['bash', '-c', 'python3.10 -m venv .venv']).wait()
    print("The virtual environment '.venv' has been created")
    override = True
elif os.path.exists('.venv'):
    while True:
        override = str(input("The virtual environment '.venv' does exist. Would you like to override it? (yes or no) "))
        if (override.upper().startswith("Y")):
            override = True
            venv_name = False
            print("Now overriding the current virtual environment.")
            Popen(['bash', '-c', 'python3.10 -m venv .venv']).wait()
            print("The virtual environment '.venv' has been created and has overridden the previous virtual environment.")
            break
        elif (override.upper().startswith("N")):
            override = False
            venv_name = str(input("What would you like the new virtual environment to be named? "))
            print(f"Now creating the virtual environment '{venv_name}'.")
            Popen(['bash', '-c', f'python3.10 -m venv {venv_name}']).wait()
            print(f"The virtual environment '{venv_name}' has been created.")
            break
        else:
            print("Please enter yes or no.")

# Activate the virtual environment and install volttron-ansible depending on whether the venv was overriden or not.
if override:
    print("Now checking if the collection 'volttron-ansible' is installed.")
    time.sleep(1)
    if not os.path.exists(os.path.expanduser("~") + "/.ansible/collections/ansible_collections/volttron"):
        print("The collection 'volttron-ansible' is not installed.")
        print("Now activating the virtual environment '.venv' and installing the collection 'volttron-ansible'.")
        Popen(['bash', '-c', 'source .venv/bin/activate && ansible-galaxy collection install git+https://github.com/VOLTTRON/volttron-ansible.git,develop']).wait()
        print("The collection 'volttron-ansible' has been installed inside the virtual environment '.venv'.")
    else:
        print("The collection 'volttron-ansible' is already installed.")
if not override:
    print("Now checking if the collection 'volttron-ansible' is installed.")
    time.sleep(1)
    if not os.path.exists(os.path.expanduser("~") + "/.ansible/collections/ansible_collections/volttron"):
        print("The collection 'volttron-ansible' has not been installed.")
        print(f"Now activating the virtual environemnt '{venv_name}' and installing the collection 'volttron-ansible'.")
        Popen(['bash', '-c', f'source {venv_name}/bin/activate && ansible-galaxy collection install git+https://github.com/VOLTTRON/volttron-ansible.git,develop']).wait()
        print(f"The collection 'volttron-ansible' has been installed inside the virtual environment '{venv_name}'.")
    else:
        print("The collection 'volttron-ansible' is already installed.")

# Clone repo so web server can access files related to the web server
print("Cloning volttron-installer repository so the web server can access required files")
Popen(['bash', '-c', 'git clone --branch develop https://github.com/VOLTTRON/volttron-installer.git']).wait()

# ----------------------------- WEB SERVER -----------------------------
import pexpect # Import pexpect as it is was installed earlier and not used until now
hostName = "localhost"
serverPort = 8080

class myServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.path = "index.html"
        
        try:
            homePage = open(self.path).read()
            self.send_response(200)
        except:
            homePage = "File not found"
            self.send_response(404)

        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes(homePage, "utf-8"))
    
    def do_POST(self):
        if self.path == "/install-base-req":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            password = parse_qs(post_data)

            # Assumes correct password is entered first time
            if not password:
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                message = {'message': 'Please enter your password'}
                self.wfile.write(json.dumps(message).encode())
            else:
                host_config_process = pexpect.spawn("ansible-playbook -K -i localhost, --connection=local volttron.deployment.host_config")
                host_config_process.expect("BECOME password: ")
                host_config_process.sendline(post_params["password"][0])
                
                host_config_process.expect(pexpect.EOF)
                print(host_config_process.before.decode())
                
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                message = {'message': 'The base requirements have been installed'}
                self.wfile.write(json.dumps(message).encode())
        
        if self.path == "/create-instance":
            Popen(['bash', '-c', 'ansible-playbook -i localhost, --connection=local volttron.deployment.install_platform']).wait()
            Popen(['bash', '-c', 'ansible-playbook -i localhost, --connection=local volttron.deployment.run_platforms']).wait()

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            message = {'message': 'A VOLTTRON instance has been created and is now running'}
            self.wfile.write(json.dumps(message).encode())
        
        if self.path == "/configure-agents":
            content_length = int(self.headers['Content-Length'])
            picked_services = self.rfile.read(content_length).decode('utf-8')
            
            print(picked_services)
            
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            message = {'message': 'Agents have been installed'}
            self.wfile.write(json.dumps(message).encode())

# Start web server and open default browser pointed to "http://localhost:8080"; Server only gets closed after KeyboardInterrupt
if __name__ =="__main__":
    print("Now starting local web server.")
    webServer = HTTPServer((hostName, serverPort), myServer)
    print("Server started at http://%s:%s" % (hostName, serverPort))

    print("Now opening local web server using default browser.")
    time.sleep(1)
    webbrowser.open(url="http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server has been closed.")