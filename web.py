from subprocess import Popen, run, call, check_output, PIPE
from http.server import BaseHTTPRequestHandler, HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import parse_qs
from socket import socket, AF_INET, SOCK_DGRAM
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

# Verify the amount of instances being installed
while True:
    num_instances = int(input("How many instances of VOLTTRON are being created (1-5)? "))
    if (num_instances < 1 or num_instances > 5):
        print("Please enter an amount between 1 and 5.")
    else:
        break

# ----------------------------- WEB SERVER -----------------------------
import pexpect # Import pexpect as it is was installed earlier and not used until now
hostName = "localhost"
serverPort = 8080

class myServer(BaseHTTPRequestHandler):
    def do_GET(self):
        # Different web page for different number of instances
        if (num_instances == 1):
            self.path = os.getcwd() + "/index.html"

            try:
                homePage = open(self.path).read()
                self.send_response(200)
            except:
                homePage = "File not found"
                self.send_response(404)

            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes(homePage, "utf-8"))
        elif (num_instances > 1):
            self.path = os.getcwd() + "/multiple_instances.html"

            try:
                homePage = open(self.path).read()
                self.send_response(200)
            except:
                homePage = "File not found"
                self.send_response(404)

            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes(homePage, "utf-8"))

            # Because the user is creating multiple instances, we need to create subdirectories for the agent_config files to sit under. (localhost1, localhost2, ..., localhost(n))
            for dir in range(1, num_instances + 1):
                Popen(['bash', '-c', f'mkdir -p localhost{dir}']).wait()

            # Create inventory file for all instances after web server has been opened
            with open(os.getcwd() + "/multiple_instances_inventory.yml", "w") as inventory:
                inventory.write("---")
                inventory.write("\nall:")
                inventory.write("\n  hosts:")
                for host in range(1, num_instances + 1):
                    inventory.write(f"\n    localhost{host}:")
                    inventory.write(f'\n      volttron_home: "~/volttron_{host}"')

            # Create forms with checkboxes dependent on the number of instances said to be installed.
            for count in range(1,num_instances + 1):
                form = f'''
                <h2>Select Services for Instance {count}</h2>
                <form onsubmit="event.preventDefault(); installPlatform{count}();" enctype="application/x-www-form-urlencoded" id="form{count}">
                    <input type="checkbox" id="agent1" name="checkbox_instance_{count}" value="ActuatorAgent">
                    <label for="agent1"> Acutator Agent</label>
                    <input type="checkbox" id="agent2" name="checkbox_instance_{count}" value="BACnetProxy">
                    <label for="agent2"> BACnet Proxy</label>
                    <br>
                    <input type="checkbox" id="agent3" name="checkbox_instance_{count}" value="DataMover">
                    <label for="agent3"> Data Mover</label>
                    <input type="checkbox" id="agent4" name="checkbox_instance_{count}" value="DNP3Agent">
                    <label for="agent4"> DNP3 Agent</label>
                    <br>
                    <input type="checkbox" id="agent5" name="checkbox_instance_{count}" value="ForwardHistorian">
                    <label for="agent5"> Forward Historian</label>
                    <input type="checkbox" id="agent6" name="checkbox_instance_{count}" value="IEEE2030_5Agent">
                    <label for="agent6"> IEEE 2030.5 Agent</label>
                    <br>
                    <input type="checkbox" id="agent7" name="checkbox_instance_{count}" value="MongodbTaggingService">
                    <label for="agent7"> MongoDB Tagging </label>
                    <input type="checkbox" id="agent8" name="checkbox_instance_{count}" value="MQTTHistorian">
                    <label for="agent8"> MQTT Historian</label>
                    <br>
                    <input type="checkbox" id="agent9" name="checkbox_instance_{count}" value="OpenADRVenAgent">
                    <label for="agent9"> OpenADR VEN Agent</label>
                    <input type="checkbox" id="agent10" name="checkbox_instance_{count}" value="PlatformDriverAgent">
                    <label for="agent10"> Platform Driver Agent</label>
                    <br>
                    <input type="checkbox" id="agent11" name="checkbox_instance_{count}" value="SQLAggregateHistorian">
                    <label for="agent11"> SQL Aggregate Historian</label>
                    <input type="checkbox" id="agent12" name="checkbox_instance_{count}" value="SQLHistorian">
                    <label for="agent12"> SQL Historian</label>
                    <br>
                    <input type="checkbox" id="agent13" name="checkbox_instance_{count}" value="SQLiteTaggingService">
                    <label for="agent13"> SQLite Tagging</label>
                    <input type="checkbox" id="agent14" name="checkbox_instance_{count}" value="VolttronCentral">
                    <label for="agent14"> VOLTTRON Central</label>
                    <br>
                    <input type="checkbox" id="agent15" name="checkbox_instance_{count}" value="VolttronCentralPlatform">
                    <label for="agent15"> VOLTTRON Central Platform</label>
                    <input type="checkbox" id="agent16" name="checkbox_instance_{count}" value="WeatherDotGov">
                    <label for="agent16"> Weather Dot Gov</label>
                    <br>
                    <input type="submit" value="Install Instance {count}" form="form{count}">
                </form>
                '''
                self.wfile.write(form.encode())

    def do_POST(self):
        if self.path == "/install-base-req":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            credentials = parse_qs(post_data)
            
            # Change to appropriate config file temporarily
            set_defaults_filepath = "~/.ansible/collections/ansible_collections/volttron/deployment/roles/set_defaults/tasks/main.yml"
            with open(os.path.expanduser(set_defaults_filepath), 'r+') as edit_set_defaults:
                lines = edit_set_defaults.readlines()

                lines[116] = "    deployment_platform_config_file: \"{{ deployment_platform_config_file | default( \'~/.ansible/collections/ansible_collections/volttron/deployment/examples/vagrant-vms/collector1/collector1.yml\' ) }}\"\n"
                edit_set_defaults.seek(0)
                edit_set_defaults.writelines(lines)
                edit_set_defaults.truncate()

            # Assumes correct password is entered first time
            if not credentials:
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                message = {'message': 'Please enter your password'}
                self.wfile.write(json.dumps(message).encode())
            else:
                host_config_process = pexpect.spawn("ansible-playbook -K -i localhost, --connection=local volttron.deployment.host_config")
                host_config_process.expect("BECOME password: ")
                host_config_process.sendline(credentials["password"][0])
                
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
            post_data = self.rfile.read(content_length).decode('utf-8')
            picked_services = json.loads(post_data)
            
            # Create config file for agents
            with open(os.getcwd() + '/agent_config.yml', 'w') as config:
                config.write("---")
                config.write("\nconfig: {}\n")
                config.write("\nagents:")

                for key, value in picked_services.items():
                    for service in value:
                        config_file = "config"

                        if service == "ActuatorAgent":
                            config.write("\n  actuator.agent:")
                        elif service == "BACnetProxy":
                            config.write("\n  bacnet.proxy:")
                        elif service == "DataMover":
                            config.write("\n  data.mover:")
                        elif service == "DNP3Agent":
                            config.write("\n  dnp3.agent:")
                        elif service == "ForwardHistorian":
                            config.write("\n  forward.historian:")
                        elif service == "IEEE2030_5Agent":
                            config.write("\n  ieee.agent:")
                        elif service == "MongodbTaggingService":
                            config.write("\n  mongodb.tagging:")
                        elif service == "MQTTHistorian":
                            config.write("\n  mqtt.historian:")
                        elif service == "OpenADRVenAgent":
                            config_file = "config_example1.json"
                            config.write("\n  openadrven.agent:")
                        elif service == "PlatformDriverAgent":
                            config.write("\n  platformdriver.agent:")
                        elif service == "SQLAggregateHistorian":
                            config.write("\n  sqlaggregate.historian:")
                        elif service == "SQLHistorian":
                            config_file = "config.sqlite"
                            config.write("\n  sql.historian:")
                        elif service == "SQLiteTaggingService":
                            config.write("\n  sqlite.tagging:")
                        elif service == "VolttronCentral":
                            config.write("\n  volttron.central:")
                        elif service == "VolttronCentralPlatform":
                            config.write("\n  vc.platform:")
                        elif service == "WeatherDotGov":
                            config.write("\n  weather.gov:")

                        config.write(f"\n    agent_source: '$VOLTTRON_ROOT/services/core/{service}'")
                        config.write(f"\n    agent_config: '$VOLTTRON_ROOT/services/core/{service}/{config_file}'")
                        config.write("\n    agent_running: True")
                        config.write("\n    agent_enabled: True\n")
            
            # Change to appropriate config file permanently
            set_defaults_filepath = "~/.ansible/collections/ansible_collections/volttron/deployment/roles/set_defaults/tasks/main.yml"
            with open(os.path.expanduser(set_defaults_filepath), 'r+') as edit_set_defaults:
                lines = edit_set_defaults.readlines()
                lines[116] = "    deployment_platform_config_file: \"{{ deployment_platform_config_file | default( '" + os.getcwd() + "/agent_config.yml' ) }}\"\n"
                edit_set_defaults.seek(0)
                edit_set_defaults.writelines(lines)
                edit_set_defaults.truncate()
            
            Popen(['bash', '-c', 'ansible-playbook -i localhost, --connection=local volttron.deployment.configure_agents']).wait()
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            message = {'message': 'Agents have been installed'}
            self.wfile.write(json.dumps(message).encode())

        # Create config files for each instance
        if self.path == "/install-platform1":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            picked_services = json.loads(post_data)

            # Get public IP for vip-address
            temp_socket = socket(AF_INET, SOCK_DGRAM)
            temp_socket.connect(('8.8.8.8', 80))
            ip = temp_socket.getsockname()[0]
            temp_socket.close()

            with open(os.getcwd() + '/localhost1/localhost1.yml', 'w') as config:
                config.write("---")
                config.write("\nconfig:")
                config.write(f"\n  vip-address: tcp://{ip}:22916\n")
                config.write("\nagents:")       
                for key, value in picked_services.items():
                    for service in value:
                        config_file = "config"
                        if service == "ActuatorAgent":
                            config.write("\n  actuator.agent:")
                        elif service == "BACnetProxy":
                            config.write("\n  bacnet.proxy:")
                        elif service == "DataMover":
                            config.write("\n  data.mover:")
                        elif service == "DNP3Agent":
                            config.write("\n  dnp3.agent:")
                        elif service == "ForwardHistorian":
                            config.write("\n  forward.historian:")
                        elif service == "IEEE2030_5Agent":
                            config.write("\n  ieee.agent:")
                        elif service == "MongodbTaggingService":
                            config.write("\n  mongodb.tagging:")
                        elif service == "MQTTHistorian":
                            config.write("\n  mqtt.historian:")
                        elif service == "OpenADRVenAgent":
                            config_file = "config_example1.json"
                            config.write("\n  openadrven.agent:")
                        elif service == "PlatformDriverAgent":
                            config.write("\n  platformdriver.agent:")
                        elif service == "SQLAggregateHistorian":
                            config.write("\n  sqlaggregate.historian:")
                        elif service == "SQLHistorian":
                            config_file = "config.sqlite"
                            config.write("\n  sql.historian:")
                        elif service == "SQLiteTaggingService":
                            config.write("\n  sqlite.tagging:")
                        elif service == "VolttronCentral":
                            config.write("\n  volttron.central:")
                        elif service == "VolttronCentralPlatform":
                            config.write("\n  vc.platform:")
                        elif service == "WeatherDotGov":
                            config.write("\n  weather.gov:")

                        config.write(f"\n    agent_source: '$VOLTTRON_ROOT/services/core/{service}'")
                        config.write(f"\n    agent_config: '$VOLTTRON_ROOT/services/core/{service}/{config_file}'")
                        config.write("\n    agent_running: True")
                        config.write("\n    agent_enabled: True\n")
                
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

        if self.path == '/install-platform2':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            picked_services = json.loads(post_data)

            # Get public IP for vip-address
            temp_socket = socket(AF_INET, SOCK_DGRAM)
            temp_socket.connect(('8.8.8.8', 80))
            ip = temp_socket.getsockname()[0]
            temp_socket.close()
        
            with open(os.getcwd() + '/localhost2/localhost2.yml', 'w') as config:
                config.write("---")
                config.write("\nconfig:")
                config.write(f"\n  vip-address: tcp://{ip}:22917\n")
                config.write("\nagents:")       
                for key, value in picked_services.items():
                    for service in value:
                        config_file = "config"
                        if service == "ActuatorAgent":
                            config.write("\n  actuator.agent:")
                        elif service == "BACnetProxy":
                            config.write("\n  bacnet.proxy:")
                        elif service == "DataMover":
                            config.write("\n  data.mover:")
                        elif service == "DNP3Agent":
                            config.write("\n  dnp3.agent:")
                        elif service == "ForwardHistorian":
                            config.write("\n  forward.historian:")
                        elif service == "IEEE2030_5Agent":
                            config.write("\n  ieee.agent:")
                        elif service == "MongodbTaggingService":
                            config.write("\n  mongodb.tagging:")
                        elif service == "MQTTHistorian":
                            config.write("\n  mqtt.historian:")
                        elif service == "OpenADRVenAgent":
                            config_file = "config_example1.json"
                            config.write("\n  openadrven.agent:")
                        elif service == "PlatformDriverAgent":
                            config.write("\n  platformdriver.agent:")
                        elif service == "SQLAggregateHistorian":
                            config.write("\n  sqlaggregate.historian:")
                        elif service == "SQLHistorian":
                            config_file = "config.sqlite"
                            config.write("\n  sql.historian:")
                        elif service == "SQLiteTaggingService":
                            config.write("\n  sqlite.tagging:")
                        elif service == "VolttronCentral":
                            config.write("\n  volttron.central:")
                        elif service == "VolttronCentralPlatform":
                            config.write("\n  vc.platform:")
                        elif service == "WeatherDotGov":
                            config.write("\n  weather.gov:")

                        config.write(f"\n    agent_source: '$VOLTTRON_ROOT/services/core/{service}'")
                        config.write(f"\n    agent_config: '$VOLTTRON_ROOT/services/core/{service}/{config_file}'")
                        config.write("\n    agent_running: True")
                        config.write("\n    agent_enabled: True\n")
                
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

        if self.path == '/install-platform3':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            picked_services = json.loads(post_data)

            # Get public IP for vip-address
            temp_socket = socket(AF_INET, SOCK_DGRAM)
            temp_socket.connect(('8.8.8.8', 80))
            ip = temp_socket.getsockname()[0]
            temp_socket.close()
        
            with open(os.getcwd() + '/localhost3/localhost3.yml', 'w') as config:
                config.write("---")
                config.write("\nconfig:")
                config.write(f"\n  vip-address: tcp://{ip}:22918\n")
                config.write("\nagents:")       
                for key, value in picked_services.items():
                    for service in value:
                        config_file = "config"
                        if service == "ActuatorAgent":
                            config.write("\n  actuator.agent:")
                        elif service == "BACnetProxy":
                            config.write("\n  bacnet.proxy:")
                        elif service == "DataMover":
                            config.write("\n  data.mover:")
                        elif service == "DNP3Agent":
                            config.write("\n  dnp3.agent:")
                        elif service == "ForwardHistorian":
                            config.write("\n  forward.historian:")
                        elif service == "IEEE2030_5Agent":
                            config.write("\n  ieee.agent:")
                        elif service == "MongodbTaggingService":
                            config.write("\n  mongodb.tagging:")
                        elif service == "MQTTHistorian":
                            config.write("\n  mqtt.historian:")
                        elif service == "OpenADRVenAgent":
                            config_file = "config_example1.json"
                            config.write("\n  openadrven.agent:")
                        elif service == "PlatformDriverAgent":
                            config.write("\n  platformdriver.agent:")
                        elif service == "SQLAggregateHistorian":
                            config.write("\n  sqlaggregate.historian:")
                        elif service == "SQLHistorian":
                            config_file = "config.sqlite"
                            config.write("\n  sql.historian:")
                        elif service == "SQLiteTaggingService":
                            config.write("\n  sqlite.tagging:")
                        elif service == "VolttronCentral":
                            config.write("\n  volttron.central:")
                        elif service == "VolttronCentralPlatform":
                            config.write("\n  vc.platform:")
                        elif service == "WeatherDotGov":
                            config.write("\n  weather.gov:")

                        config.write(f"\n    agent_source: '$VOLTTRON_ROOT/services/core/{service}'")
                        config.write(f"\n    agent_config: '$VOLTTRON_ROOT/services/core/{service}/{config_file}'")
                        config.write("\n    agent_running: True")
                        config.write("\n    agent_enabled: True\n")
                
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

        if self.path == '/install-platform4':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            picked_services = json.loads(post_data)

            # Get public IP for vip-address
            temp_socket = socket(AF_INET, SOCK_DGRAM)
            temp_socket.connect(('8.8.8.8', 80))
            ip = temp_socket.getsockname()[0]
            temp_socket.close()
        
            with open(os.getcwd() + '/localhost4/localhost4.yml', 'w') as config:
                config.write("---")
                config.write("\nconfig:")
                config.write(f"\n  vip-address: tcp://{ip}:22919\n")
                config.write("\nagents:")       
                for key, value in picked_services.items():
                    for service in value:
                        config_file = "config"
                        if service == "ActuatorAgent":
                            config.write("\n  actuator.agent:")
                        elif service == "BACnetProxy":
                            config.write("\n  bacnet.proxy:")
                        elif service == "DataMover":
                            config.write("\n  data.mover:")
                        elif service == "DNP3Agent":
                            config.write("\n  dnp3.agent:")
                        elif service == "ForwardHistorian":
                            config.write("\n  forward.historian:")
                        elif service == "IEEE2030_5Agent":
                            config.write("\n  ieee.agent:")
                        elif service == "MongodbTaggingService":
                            config.write("\n  mongodb.tagging:")
                        elif service == "MQTTHistorian":
                            config.write("\n  mqtt.historian:")
                        elif service == "OpenADRVenAgent":
                            config_file = "config_example1.json"
                            config.write("\n  openadrven.agent:")
                        elif service == "PlatformDriverAgent":
                            config.write("\n  platformdriver.agent:")
                        elif service == "SQLAggregateHistorian":
                            config.write("\n  sqlaggregate.historian:")
                        elif service == "SQLHistorian":
                            config_file = "config.sqlite"
                            config.write("\n  sql.historian:")
                        elif service == "SQLiteTaggingService":
                            config.write("\n  sqlite.tagging:")
                        elif service == "VolttronCentral":
                            config.write("\n  volttron.central:")
                        elif service == "VolttronCentralPlatform":
                            config.write("\n  vc.platform:")
                        elif service == "WeatherDotGov":
                            config.write("\n  weather.gov:")

                        config.write(f"\n    agent_source: '$VOLTTRON_ROOT/services/core/{service}'")
                        config.write(f"\n    agent_config: '$VOLTTRON_ROOT/services/core/{service}/{config_file}'")
                        config.write("\n    agent_running: True")
                        config.write("\n    agent_enabled: True\n")
                
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

        if self.path == '/install-platform5':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            picked_services = json.loads(post_data)

            # Get public IP for vip-address
            temp_socket = socket(AF_INET, SOCK_DGRAM)
            temp_socket.connect(('8.8.8.8', 80))
            ip = temp_socket.getsockname()[0]
            temp_socket.close()
        
            with open(os.getcwd() + '/localhost5/localhost5.yml', 'w') as config:
                config.write("---")
                config.write("\nconfig:")
                config.write(f"\n  vip-address: tcp://{ip}:22920\n")
                config.write("\nagents:")       
                for key, value in picked_services.items():
                    for service in value:
                        config_file = "config"
                        if service == "ActuatorAgent":
                            config.write("\n  actuator.agent:")
                        elif service == "BACnetProxy":
                            config.write("\n  bacnet.proxy:")
                        elif service == "DataMover":
                            config.write("\n  data.mover:")
                        elif service == "DNP3Agent":
                            config.write("\n  dnp3.agent:")
                        elif service == "ForwardHistorian":
                            config.write("\n  forward.historian:")
                        elif service == "IEEE2030_5Agent":
                            config.write("\n  ieee.agent:")
                        elif service == "MongodbTaggingService":
                            config.write("\n  mongodb.tagging:")
                        elif service == "MQTTHistorian":
                            config.write("\n  mqtt.historian:")
                        elif service == "OpenADRVenAgent":
                            config_file = "config_example1.json"
                            config.write("\n  openadrven.agent:")
                        elif service == "PlatformDriverAgent":
                            config.write("\n  platformdriver.agent:")
                        elif service == "SQLAggregateHistorian":
                            config.write("\n  sqlaggregate.historian:")
                        elif service == "SQLHistorian":
                            config_file = "config.sqlite"
                            config.write("\n  sql.historian:")
                        elif service == "SQLiteTaggingService":
                            config.write("\n  sqlite.tagging:")
                        elif service == "VolttronCentral":
                            config.write("\n  volttron.central:")
                        elif service == "VolttronCentralPlatform":
                            config.write("\n  vc.platform:")
                        elif service == "WeatherDotGov":
                            config.write("\n  weather.gov:")

                        config.write(f"\n    agent_source: '$VOLTTRON_ROOT/services/core/{service}'")
                        config.write(f"\n    agent_config: '$VOLTTRON_ROOT/services/core/{service}/{config_file}'")
                        config.write("\n    agent_running: True")
                        config.write("\n    agent_enabled: True\n")
                
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
        
        # Start and stop volttron instance (only for 1 instance currently)
        if self.path == "/start-volttron":
            Popen(['bash', '-c', 'cd ~/volttron && ./start-volttron']).wait()

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            message = {'message': 'VOLTTRON has been started'}
            self.wfile.write(json.dumps(message).encode())
        
        if self.path == "/stop-volttron":
            Popen(['bash', '-c', 'cd ~/volttron && ./stop-volttron']).wait()

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            message = {'message': 'VOLTTRON has been stopped'}
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