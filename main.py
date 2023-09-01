from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from enum import Enum
from multiprocessing import Manager, Queue
from nicegui import app, ui
from shutil import rmtree
from subprocess import PIPE, Popen
from typing import List, Optional
from yaml import dump, safe_load

import asyncio
import json
import os

pool = ProcessPoolExecutor()

# Create Enum's for each attribute of agent with defaults (used for easy mapping and data modification)
class AgentName(Enum):
    '''Enum of Agent Names'''
    NAME_ACTUATOR = "Actuator Agent"
    NAME_BACNET = "BACnet Proxy"
    NAME_DATA_MOVER = "Data Mover"
    NAME_DNP3 = "DNP3 Agent"
    NAME_FORWARD_HIST = "Forward Historian"
    NAME_IEEE = "IEEE 2030.5 Agent"
    NAME_MONGODB_TAGGING = "MongoDB Tagging Service"
    NAME_MQTT_HIST = "MQTT Historian"
    NAME_OPENADR_VEN = "OpenADR VEN Agent"
    NAME_PLATFORM_DRIVER = "Platform Driver Agent"
    NAME_SQL_AGG_HIST = "SQL Aggregate Historian"
    NAME_SQL_HIST = "SQL Historian"
    NAME_SQLITE_TAGGING = "SQLite Tagging Service"
    NAME_VOLTTRON_CENTRAL = "VOLTTRON Central"
    NAME_VOLTTRON_CENTRAL_PLATFORM = "VOLTTRON Central Platform"
    NAME_WEATHER_DOT_GOV = "Weather Dot Gov"

class AgentIdentity(Enum):
    '''Enum of Agent Identities'''
    ID_ACTUATOR = "platform.actuator"
    ID_BACNET = "platform.bacnet_proxy"
    ID_DATA_MOVER = "platform.datamover"
    ID_DNP3 = "platform.dnp3"
    ID_FORWARD_HIST = "platform.forward"
    ID_IEEE = "IEEE2030_5agent"
    ID_MONGODB_TAGGING = "platform.mongodb"
    ID_MQTT_HIST = "platform.mqtt"
    ID_OPENADR_VEN = "platform.openadr"
    ID_PLATFORM_DRIVER = "platform.driver"
    ID_SQL_AGG_HIST = "platform.sqlagg"
    ID_SQL_HIST = "platform.sql"
    ID_SQLITE_TAGGING = "platform.sqlite"
    ID_VOLTTRON_CENTRAL = "volttron.central"
    ID_VOLTTRON_CENTRAL_PLATFORM = "platform.agent"
    ID_WEATHER_DOT_GOV = "platform.weatherdotgov"

SOURCE_PATH = "$VOLTTRON_ROOT/services/core/"
class AgentSource(Enum):
    '''Enum of Agent Sources'''
    SOURCE_ACTUATOR = SOURCE_PATH + "ActuatorAgent"
    SOURCE_BACNET = SOURCE_PATH + "BACnetProxy"
    SOURCE_DATAMOVER = SOURCE_PATH + "DataMover"
    SOURCE_DNP3 = SOURCE_PATH + "DNP3Agent"
    SOURCE_FORWARDHIST = SOURCE_PATH + "ForwardHistorian"
    SOURCE_IEEE = SOURCE_PATH + "IEEE2030_5Agent"
    SOURCE_MONGODB = SOURCE_PATH + "MongodbTaggingService"
    SOURCE_MQTTHIST = SOURCE_PATH + "MQTTHistorian"
    SOURCE_OPENADR = SOURCE_PATH + "OpenADRVenAgent"
    SOURCE_PLATFORMDRIVER = SOURCE_PATH + "PlatformDriverAgent"
    SOURCE_SQLAGG = SOURCE_PATH + "SQLAggregateHistorian"
    SOURCE_SQL = SOURCE_PATH + "SQLHistorian"
    SOURCE_SQLITE = SOURCE_PATH + "SQLiteTaggingService"
    SOURCE_VC = SOURCE_PATH + "VolttronCentral"
    SOURCE_VCPLATFORM = SOURCE_PATH + "VolttronCentralPlatform"
    SOURCE_WEATHERDOTGOV = SOURCE_PATH + "WeatherDotGov"

class AgentConfig(Enum):
    '''Enum of Agent Configs'''
    CONFIG_ACTUATOR = {
        "schedule_publish_interval": 30,
        "schedule_state_file": "actuator_state.pickle"
    }
    CONFIG_BACNET = {
        "device_address": "10.0.2.15", # Need to pull ip of host computer
        "max_apdu_length": 1024,
        "object_id": 599,
        "object_name": "Volttron BACnet driver",
        "vendor_id": 15,
        "segmentation_supported": "segmentedBoth"
    }
    CONFIG_DATAMOVER = {
        "destination-serverkey": None,
        "destination-vip": "tcp://127.0.0.1:23916",
        "destination-historian-identity": "platform.historian",
        "remote-identity": "22916.datamover"
    }
    CONFIG_DNP3 = {
        "points": "config://mesa_points.config",
        "point_topic": "dnp3/point",
        "outstation_status_topic": "dnp3/outstation_status",
        "outstation_config": {
            "database_sizes": 10000,
            "log_levels": ["NORMAL"]
        },
        "local_ip": "0.0.0.0",
        "port": 20000
    }
    CONFIG_FORWARDHIST = {
        "destination-serverkey": None,
        "destination-vip": "tcp://127.0.0.1:22916",
        "required_target_agents": [],
        "capture_device_data": True,
        "capture_analysis_data": True,
        "capture_log_data": True,
        "capture_record_data": True,
        "custom_topic_list": ["actuator", "alert"],
        "cache_only": False,
        "message_publish_count": 10000

    }
    CONFIG_IEEE = {
        "devices": [
            {
                "sfdi": "097935300833",
                "lfdi": "247bd68e3378fe57ba604e3c8bdf9e3f78a3d743",
                "load_shed_device_category": "0200",
                "pin_code": "130178"
            },
            {
                "sfdi": "111576577659",
                "lfdi": "2990c58a59935a7d5838c952b1a453c967341a07",
                "load_shed_device_category": "0200",
                "pin_code": "130178"
            }
        ],
        "IEEE2030_5_server_sfdi": "413707194130",
        "IEEE2030_5_server_lfdi": "29834592834729384728374562039847629",
        "load_shed_device_category": "0020",
        "timezone": "America/Los_Angeles"

    }
    CONFIG_MONGODB = {
        "connection": {
            "type": "mongodb",
            "params": {
                "host": "localhost",
                "port": 27017,
                "database": "mongo_test",
                "user": "test",
                "passwd": "test"
            }
        }
    }
    CONFIG_MQTTHIST = {
        "connection": {
            "mqtt_hostname": "localhost",
            "mqtt_port": 1883
        }
    }
    CONFIG_OPENADR = {
        "ven_name": "PNNLVEN",
        "vtn_url": "https://eiss2demo.ipkeys.com/oadr2/OpenADR2/Simple/2.0b",
        "openadr_client_type": "IPKeysClient"
    }
    CONFIG_PLATFORMDRIVER = {
        "driver_scrape_interval": 0.05,
        "publish_breadth_first_all": False,
        "publish_depth_first": False,
        "publish_breadth_first": False
    }
    CONFIG_SQLAGG = {
        "connection": {
            "type": "sqlite",
            "params": {
                "database": "test.sqlite",
                "timeout": 15
            }
        },
        "aggregations":[
            {
                "aggregation_period": "1m",
                "use_calendar_time_periods": "true",
                    "points": [
                        {
                            "topic_names": ["device1/out_temp"],
                            "aggregation_type": "sum",
                            "min_count": 2
                        },
                        {
                            "topic_names": ["device1/in_temp"],
                            "aggregation_type": "sum",
                            "min_count": 2
                        }
                ]
            },
            {
                "aggregation_period": "2m",
                "use_calendar_time_periods": "false",
                    "points": [
                        {
                            "topic_names": ["device1/out_temp"],
                            "aggregation_type": "sum",
                            "min_count": 2
                        },
                        {
                            "topic_names": ["device1/in_temp"],
                            "aggregation_type": "sum",
                            "min_count": 2
                        }
                ]
            }
        ]
    }
    CONFIG_SQL = {
        "connection": {
            "type": "sqlite",
            "params": {
                "database": "historian_test.sqlite"
            }
        },
        "all_platforms": True
    }
    CONFIG_SQLITE = {
        "connection": {
            "type": "sqlite",
            "params": {
                "database": "~/.volttron/data/volttron.tags.sqlite"
            }
        }
    }
    CONFIG_VC = {"webroot": "path/to/webroot"} # Default has no config; Putting in optional config to fix listing issue
    CONFIG_VCPLATFORM = {} # Default is no config
    CONFIG_WEATHERDOTGOV = {
        "database_file": "weather.sqlite",
        "max_size_gb": 1,
        "poll_locations": [{"station": "KLAX"}, {"station": "KPHX"}],
        "poll_interval": 60
    }

@dataclass
class Agent:
    '''Class for Agents'''
    name: str
    identity: str
    source: str
    config: str

@dataclass
class Instance:
    '''Class for an Instance'''
    name: str
    vip_address: str = "tcp://127.0.0.1:22916"
    bind_web_address: Optional[str] = None
    agents: List[Agent] = field(default_factory=[])

    def write_platform_config(self):
        '''Write Platform Config File'''
        if self.bind_web_address is not None:
            platform_dict = {
                "config": {
                    "vip_address": self.vip_address,
                    "bind_web_address": self.bind_web_address,
                },
                "agents": {}
            }
        else:
            platform_dict = {
                "config": {
                    "vip_address": self.vip_address,
                },
                "agents": {}
            }

        os.makedirs(os.path.expanduser("~") + f"/.volttron_installer/platforms/{self.name}", exist_ok=True)
        os.makedirs(os.path.expanduser("~") + f"/.volttron_installer/platforms/{self.name}/agent_configs", exist_ok=True)

        for agent in self.agents:
            for num in range(0, 16):
                if list(AgentName)[num].value == agent.name:
                    config_str = str(agent.config)
                    config = config_str.replace("'", "\"").replace("False", "false").replace("True", "true").replace("None", "null") # Change single quotes to double so str can be converted to dict

                    # Create agent config files
                    id = agent.identity.replace(".", "_")
                    with open(os.path.expanduser("~") + f'/.volttron_installer/platforms/{self.name}/agent_configs/{id}_config', 'w') as agent_config:
                        agent_config.write(config)

                    agent_config_path = os.path.expanduser("~") + f'/.volttron_installer/platforms/{self.name}/agent_configs/{id}_config'
                    agent.config = agent_config_path
                num += 1

            platform_dict['agents'].update({
                agent.identity: {
                    "agent_source": agent.source,
                    "agent_config": agent.config,
                    "agent_running": True,
                    "agent_enabled": True
                }
            })

        with open(os.path.expanduser("~") + f'/.volttron_installer/platforms/{self.name}/{self.name}.yml', 'w') as platform_config_file:
            dump(platform_dict, platform_config_file)
    
    @staticmethod
    def read_platform_config(instances: List[str]) -> 'Instance':
        '''Read Saved Platform Config File'''
        machine_list = []
        ip_list = []
        instance_obj = Instance(name="", vip_address="", bind_web_address="", agents=[])
        
        with open(os.path.expanduser("~/.volttron_installer/platforms/machines.yml"), 'r') as machines_config:
            machines_dict = safe_load(machines_config.read())

            for machine, ip in machines_dict['machines'].items():
                machine_list.append(machine)
                ip_list.append(ip['ip'])

        for instance in instances:
            agent_list = []

            with open(os.path.expanduser("~") + f'/.volttron_installer/platforms/{instance}/{instance}.yml', 'r') as platform_config_file:
                platform_dict = safe_load(platform_config_file.read())

            # Get variables needed for the platform object; Used for frontend
            vip_address = platform_dict['config']['vip_address']

            if 'bind_web_address' in platform_dict['config']:
                bind_web_address = platform_dict['config']['bind_web_address']
            else:
                bind_web_address = None

            for agent_identity, config in platform_dict['agents'].items():
                for num in range(0, 16):
                    if agent_identity == list(AgentIdentity)[num].value:
                        agent_name = list(AgentName)[num].value

                        with open(config['agent_config'], 'r') as config_file:
                            data = config_file.read()
                            agent_config = json.loads(data)

                        picked_agent = Agent(name=agent_name, identity=agent_identity, source=config['agent_source'], config=agent_config)
                        agent_list.append(picked_agent)

            instance_obj.name = instance
            instance_obj.vip_address = vip_address
            instance_obj.bind_web_address = bind_web_address
            instance_obj.agents.append(agent_list)

        return instance_obj
            
@dataclass
class Inventory:
    '''Class to Create and Read Inventory;'''
    hosts: List[str]

    def write_inventory(self, filename: str):
        '''Write Inventory File'''
        count  = 0
        inventory_dict = {
            "all": {
                "hosts": {}
            }
        }

        # Add multiple hosts with their address' to the inventory dictionary; Currently meant for one platform
        for host in self.hosts:
            count += 1
            if host == "localhost":
                inventory_dict['all']['hosts'].update({
                    host: {
                        "ansible_host": "localhost",
                        "volttron_home": f"volttron_home{count}"
                    }
                })
            else:
                inventory_dict['all']['hosts'].update({
                    host: {
                        "volttron_home": f"volttron_home{count}"
                    }
                })
        
        with open(os.path.expanduser("~") + f"/.volttron_installer/platforms/{filename}.yml", 'w') as inventory_file:
            dump(inventory_dict, inventory_file)

    @staticmethod    
    def read_inventory(filename: str) -> 'Inventory':
        '''Read Saved Inventory File'''
        with open(os.path.expanduser("~") + f"/.volttron_installer/platforms/{filename}.yml", 'r') as inventory_file:
            inventory_dict = safe_load(inventory_file.read())  

            hosts = list(inventory_dict['all']['hosts'].keys())
            inventory_obj = Inventory(hosts=hosts)

            return inventory_obj
 
# Create list and dicts to hold specific values for agents; used for modification of platform/frontend
agent_name_list = []
agent_identity_dict = {}
agent_config_dict = {}

for count in range(len(list(AgentName))):
    agent_name_list.append(list(AgentName)[count].value)
    agent_identity_dict[list(AgentName)[count].value] = list(AgentIdentity)[count].value
    agent_config_dict[list(AgentName)[count].value] = str(list(AgentConfig)[count].value)

import pexpect # Move import when code is more finished
def install_platform(q: Queue, platform: Instance, password: str):
    '''Installs platform and updates progress bar as processes are finished'''
    create_files(platform)
    q.put_nowait(20) # Update progress bar

    ## Host Configuration; handles password input; Assumes password was entered correctly
    #host_config_process = pexpect.spawn("ansible-playbook -K -i inventory.yml --connection=local volttron.deployment.host_config")
    #host_config_process.expect("BECOME password: ")
    #host_config_process.sendline(password)

    #host_config_process.expect(pexpect.EOF)
    #print(host_config_process.before.decode())
    #q.put_nowait(40)

    ## Install Platform
    #install_cmd = Popen(['bash', '-c', 'ansible-playbook -i inventory.yml --connection=local volttron.deployment.install_platform'], stdout=PIPE, stderr=PIPE)
    #stdout, stderr = install_cmd.communicate()

    #if stdout is not None:
    #    stdout_str = stdout.decode('utf-8')
    #    print(stdout_str)
    #if stderr is not None:
    #    stderr_str = stderr.decode('utf-8')
    #    print(stderr_str)

    #q.put_nowait(60)

    ## Run Platform
    #run = Popen(['bash', '-c', 'ansible-playbook -i inventory.yml --connection=local volttron.deployment.run_platforms -vvv'])
    #stdout, stderr = run.communicate()
    #
    #if stdout is not None:
    #    stdout_str = stdout.decode("utf-8")
    #    print(stdout_str)
    #if stderr is not None:
    #    stderr_str = stderr.decode("utf-8")
    #    print(stderr_str)

    #q.put_nowait(80)

    ## Configure Agents
    #configure = Popen(['bash', '-c', 'ansible-playbook -i inventory.yml --connection=local volttron.deployment.configure_agents -vvv'])
    #stdout, stderr = configure.communicate()
    #
    #if stdout is not None:
    #    stdout_str = stdout.decode('utf-8')
    #    print(stdout_str)
    #if stderr is not None:
    #    stderr_str = stderr.decode('utf-8')
    #    print(stderr_str)

    #q.put_nowait(100)

def create_files(platform: Instance):    
    '''Add sources to selected agents, create objects of those agents, append those objects to a list, and create config files'''
    
    # Create parent directory that any other file created will sit in for utilization; Make directories for agent configuration files and so ansible expects localhost.yml in correct location; Currently for one platform
    os.makedirs(os.path.expanduser("~") + f"/.volttron_installer/platforms/", exist_ok=True)

    for index, instance in enumerate(platform.instances):
        os.makedirs(os.path.expanduser("~") + f"/.volttron_installer/platforms/{instance}", exist_ok=True)
        os.makedirs(os.path.expanduser("~") + f"/.volttron_installer/platforms/{instance}/agent_configs", exist_ok=True)

        for agent in platform.agents[index]:
            for num in range(0, 16):
                if list(AgentName)[num].value == agent.name:
                    config_str = str(agent.config)
                    config = config_str.replace("'", "\"").replace("False", "false").replace("True", "true").replace("None", "null") # Change single quotes to double so str can be converted to dict

                    # Create agent config files
                    id = agent.identity.replace(".", "_")
                    with open(os.path.expanduser("~") + f'/.volttron_installer/platforms/{instance}/agent_configs/{id}_config', 'w') as agent_config:
                        agent_config.write(config)

                    agent_config_path = os.path.expanduser("~") + f'/.volttron_installer/platforms/{instance}/agent_configs/{id}_config'
                    agent.config = agent_config_path
                num += 1

    # Create inventory file
    inventory = Inventory(platform.instances)
    inventory.write_inventory("inventory")

    # Create platform configuration file after inventory;
    platform.write_platform_config(inventory.hosts)
    
    return platform

# --------------------------------------------- WEB SIDE ---------------------------------------------

# Columns for agent tables; Constant variable
AGENT_COLUMNS = [
    {'name': 'name', 'label': 'Name', 'field': 'name', 'required': True},
    {'name': 'identity', 'label': 'Identity', 'field': 'identity', 'required': False},
    {'name': 'config', 'label': 'Configuration', 'field': 'config', 'required': False}
]

host_list = []
instance_list = []
platform_number = 1

def add_header():
    '''Add header'''
    header_items = {
        'Home': '/',
        'Machines': '/machines',
        'Instances': '/instances',
        'How To': '/howto'
    }

    with ui.header():
        with ui.row():
            for title, target in header_items.items():
                ui.link(title, target).classes(replace="text-lg text-white")

def update_choice(new_name, new_id, new_config): # Pass through objects
    '''Updates the values for identity and config input based on which agent was picked'''
    new_id.value = agent_identity_dict[new_name.value]
    new_config.value = str(agent_config_dict[new_name.value])

    new_id.update()
    new_config.update()

def remove_platform(name):
    '''Removes old platform files when changes are saved or platform is deleted'''
    rmtree(os.path.expanduser("~") + "/.volttron_installer/platforms/" + name)

def confirm_platform(old_platform_name: Optional[str] = None):
    '''Shows what the user has chosen and can be submitted'''
    async def start_installation():
        '''Async event handler; Will install platform'''
        progress.visible = True
        loop = asyncio.get_running_loop()
 
        await loop.run_in_executor(pool, install_platform, queue, platform, password.value)
 
    async def create_platform(original_platform_name: Optional[str] = None):
        '''Start installation of platform; Remove old platform files if platform is being edited'''
        if original_platform_name is None:
            await start_installation()
        else:
            remove_platform(original_platform_name)
            await start_installation()
 
    queue = Manager().Queue()

    # Output web address if checkbox was clicked
    ui.label("Overview of Configuration").style("font-size: 26px")
    with ui.row():
        ui.label("Platform Name:")
        ui.label(platform.name)
    ui.separator()

    with ui.row():
        ui.label("Hostname:")
        ui.label(platform.hostname)
    ui.separator()
    
    ui.label("Instances").style("font-size: 20px;")
    for index, instance in enumerate(platform.instances):
        rows = []
        for agent in platform.agents[index]:
            rows.append({'name': agent.name, 'identity': agent.identity, 'config': str(agent.config)})

        with ui.row():
            ui.label("Instance Name:")
            ui.label(instance)
        ui.separator()

        with ui.row():
            ui.label("VIP Address:")
            ui.label(platform.vip_address[index])
        ui.separator()

        with ui.row():
            ui.label("Web Address:")
            ui.label(str(platform.bind_web_address[index]))
        ui.separator()

        with ui.row():
            ui.table(title='Agents', columns=AGENT_COLUMNS, rows=rows)
        ui.separator()
        
    ui.label("Enter your password then click 'Confirm' to start the installation process")
    with ui.row():
        password = ui.input(placeholder="Password", label="Password", password=True, password_toggle_button=True, validation={'Please enter your password': lambda value: value.strip()})
        ui.button("Cancel", on_click=lambda: ui.open(create))
        ui.button("Confirm", on_click=lambda: create_platform(old_platform_name))
        progress = ui.circular_progress(min=0, max=100, value=0, size="xl").props('instant-feedback')
        progress.visible = False
        
    ui.timer(0.1, callback=lambda: progress.set_value(queue.get() if not queue.empty() else progress.value))

def agent_table(rows):
    '''Table for selecting agents'''
    with ui.table(title='Agents', columns=AGENT_COLUMNS, rows=rows, row_key='name', selection='multiple').classes('w-75') as table:
        with table.add_slot('header'):
            with table.row():
                with table.cell():
                    ui.button(on_click=lambda: (
                        table.add_rows({'name': new_name.value, 'identity': new_id.value, 'config': new_config.value}),
                        new_name.set_value(list(AgentName)[0].value),
                        new_id.set_value(list(AgentIdentity)[0].value),
                        new_config.set_value(str(list(AgentConfig)[0].value)),
                        table.update()
                    ), icon='add').props('flat fab-mini')
                with table.cell():
                    new_name = ui.select(agent_name_list, value=agent_name_list[0], on_change=lambda: update_choice(new_name, new_id, new_config))
                with table.cell():
                    new_id = ui.input(label="Identity", value=agent_identity_dict[new_name.value])
                with table.cell():
                    new_config = ui.input(label="Configuration", value=agent_config_dict[new_name.value])

    ui.button('Remove', on_click=lambda: table.remove_rows(*table.selected)) \
        .bind_visibility_from(table, 'selected', backward=lambda val: bool(val))
    
    return table
    
def platform_table():
    '''Table to display installed platforms; Allows editing of platforms and agents'''
    platform_columns = [
        {'name': 'name', 'label': 'Name', 'field': 'name', 'sortable': True},
        {'name': 'num_instances', 'label': '# of Instances', 'field': 'num_instances'},
        {'name': 'num_agents', 'label': '# of Agents', 'field': 'num_agents'},
        #{'name': 'date_created', 'label': 'Date Created', 'field': 'date_created'}
    ]

    platform_rows = []
    global instance_list
    instance_list = []
    num_agents = 0

    # Get inventory and plaform config obj's from saved files; Append info from inventory and platform config to table rows of platforms
    platforms_path = os.path.expanduser("~") + "/.volttron_installer/platforms/"
    for instance_dir in os.listdir(platforms_path):
        num_agents = 0
        if os.path.isdir(platforms_path + instance_dir):
            instance_list.append(instance_dir)
            inventory = Inventory.read_inventory("inventory")
            platform = Instance.read_platform_config(inventory.hosts)
            platform.hostname = inventory.hostname

            print(platform)
            for index, instance in enumerate(platform.instances):
                if instance == instance_dir:
                    for agent_list in platform.agents[index]:
                        num_agents += 1

            platform_rows.append({'name': platform.name, 'num_instances': len(instance_list), 'num_agents': num_agents})

    table = ui.table(title="Platforms", columns=platform_columns, rows=platform_rows, row_key="name", selection="single")
    
    return table

def machine_table(rows):
    machine_columns = [
        {'name': 'name', 'label': 'Machine Name', 'field': 'name', 'sortable': True},
        {'name': 'ip_address', 'label': 'IP Address', 'field': 'ip_address', 'sortable': True},
        #{'name': 'date_created', 'label': 'Date Created', 'field': 'date_created'}
    ]

    def add_machine(name: str, ip: str):
        if os.path.exists(os.path.expanduser("~") + "/.volttron_installer/platforms/machines.yml"):
            with open(os.path.expanduser("~") + '/.volttron_installer/platforms/machines.yml', 'r') as machines_file:
                machines_dict = safe_load(machines_file.read())
                
            machines_dict['machines'].update({
                name: {
                    'ip': ip
                }
            })
            
            with open(os.path.expanduser("~") + '/.volttron_installer/platforms/machines.yml', 'w') as machines_file:
                dump(machines_dict, machines_file)

        else:
            with open(os.path.expanduser("~") + '/.volttron_installer/platforms/machines.yml', 'w') as machines_file:
                machines_dict = {
                    "machines": {
                        name: {
                            'ip': ip
                        }
                    }
                }
                dump(machines_dict, machines_file)

    table = ui.table(title='Host Machines', columns=machine_columns, rows=rows, row_key='machine_name', selection='single').classes('w-75')
    with table.add_slot('header'):
        with table.row():
            with table.cell():
                ui.button(on_click=lambda: (
                    table.add_rows({'name': str(new_name.value), 'ip_address': new_ip.value}),
                    add_machine(new_name.value, new_ip.value),
                    new_name.set_value(""),
                    new_ip.set_value(""),
                    table.update()
                ), icon='add').props('flat fab-mini')
            with table.cell():
                new_name = ui.input(label="Machine Name")
            with table.cell():
                new_ip = ui.input(label="IP Address")

def instance_table(rows):
    instance_columns = [
        {'name': 'name', 'label': 'Instance Name', 'field': 'name', 'sortable': True},
        #{'name': 'date_created', 'label': 'Date Created', 'field': 'date_created'}
    ]
    def open_instance_page(instance: str):
        '''Creates endpoint required for instance edit page and opens the instance edit page'''
        instance_str = instance.replace("'", "\"")
        instance_list = json.loads(instance_str)
        original_instance_name = instance_list[0]['name']

        ui.open(f"http://127.0.0.1:8080/edit/{original_instance_name }")

    with ui.table(title='Instances', columns=instance_columns, rows=rows, row_key='name', selection='single').classes('w-75') as table:
        with table.add_slot('header'):
            with table.row():
                with table.cell():
                    ui.button(on_click=lambda: (
                        table.add_rows({'name': str(new_name.value)}),
                        new_name.set_value(""),
                        table.update()
                    ), icon='add').props('flat fab-mini')
                with table.cell():
                    new_name = ui.input(label="Instance Name")

    with ui.row().bind_visibility_from(table, 'selected', backward=lambda val: bool(val)):
        ui.button('Edit', on_click=lambda: open_instance_page(label.text))
        ui.button('Remove', on_click=lambda: confirm_remove(label.text))
    
    with ui.row():
        ui.label("Current Selection:")
        label = ui.label().bind_text_from(table, 'selected', lambda val: str(val))

def default_home_page(table):
        with ui.row():
            ui.label("There are no host machines added or instances installed.")
            ui.button("Add a Host Machine", on_click=lambda: add_machine(table))

def home_page():
    add_header()        

    global platform
    inventory = Inventory.read_inventory("inventory")
    platform = Platform.read_platform_config(inventory.hosts)
    def open_edit_page(platform: str):
        '''Creates endpoint required for edit page and opens the edit page'''
        platform_str = platform.replace("'", "\"")
        platform_list = json.loads(platform_str)
        original_platform_name = platform_list[0]['name']

        ui.open(f"http://127.0.0.1:8080/edit/{original_platform_name + '?update=False'}")

    def handle_confirm_remove(original_platform_name: str, dialog):
        '''Handles on_click event when user confirms the removal of a platform'''
        # Remove row where platform was being displayed
        table.remove_rows(*table.selected)
        table.selected.clear()

        remove_platform(original_platform_name)

        dialog.close()

    def confirm_remove(platform):
        '''Confirmation of platform removal'''
        # Get old platform name for overriding
        platform_str = platform.replace("'", "\"")
        platform_list = json.loads(platform_str)
        original_platform_name = platform_list[0]['name']

        with ui.dialog() as dialog, ui.card():
            ui.label("Confirm?").style("font-size: 20px")
            ui.label(f"Are you sure you want to remove the {original_platform_name} platform? This action cannot be undone.")

            with ui.row():
                ui.button("Cancel", on_click=dialog.close)
                ui.button("Confirm", on_click=lambda: handle_confirm_remove(original_platform_name, dialog))
        dialog.open()
        

    #table = machine_table(rows=)
    with ui.row().bind_visibility_from(table, 'selected', backward=lambda val: bool(val)):
        ui.button('Edit', on_click=lambda: open_edit_page(label.text))
        ui.button('Remove', on_click=lambda: confirm_remove(label.text))
    
    with ui.row():
        ui.label("Current Selection:")
        label = ui.label().bind_text_from(table, 'selected', lambda val: str(val))


def add_instance(platform_name: str, hostname: str, instance_list: list):
    '''Adds instance to instance list and opens configuration page for that instance'''
    if instance_list == []:
        instance_name = "instance1"
        instance_list.append(instance_name)
        ui.open(f"http://127.0.0.1:8080/create/{platform_name}/{hostname}/{instance_name}")
    else:    
        instance_name = f"instance{len(instance_list) + 1}"
        instance_list.append(instance_name)
        ui.open(f"http://127.0.0.1:8080/create/{platform_name}/{hostname}/{instance_name}")

# Make a global platform obj that will be used so each host can append configurations to the overall platform
def save_instance_create(platform_name: str, hostname: str, instance_name: str, vip_address: str, checkbox: bool, table_rows: List[dict]):
    '''Save instance configuration and append values to an object; Called when instance is added on create page'''
    agent_list = []
    for agent in table_rows:
        for num in range(0, 16):
            if list(AgentName)[num].value in agent['name']:
                agent["source"] = list(AgentSource)[num].value

                #id = agent["identity"].replace(".", "_")
                #agent_config_path = os.path.expanduser("~") + f'/.volttron_installer/platforms/{platform_name}/agent_configs/{hostname}/{id}_config'

                # Append to list of agents
                picked_agent = Agent(
                    name=agent["name"],
                    identity=agent["identity"],
                    source=agent["source"],
                    config=agent["config"]
                )
                agent_list.append(picked_agent)

    platform.name = platform_name
    platform.hostname = hostname
    platform.instances.append(instance_name)
    platform.vip_address.append(vip_address)
    
    if checkbox is True:
        web_address = vip_address.replace(vip_address.split("://")[0], "http")
        platform.bind_web_address.append(web_address)
    else:
        platform.bind_web_address.append(None)

    platform.agents.append(agent_list)
    ui.open(create)

def save_instance_edit(platform_name: str, hostname: str, old_instance_name, instance_name: str, vip_address: str, checkbox: bool, table_rows: List[dict]):
    '''Save instance configuration and append values to an object; Called when adding an instance on edit page'''
    global platform
    print(platform)
    agent_list = []
    for agent in table_rows:
        for num in range(0, 16):
            if list(AgentName)[num].value in agent['name']:
                agent["source"] = list(AgentSource)[num].value

                # Append to list of agents
                picked_agent = Agent(
                    name=agent["name"],
                    identity=agent["identity"],
                    source=agent["source"],
                    config=agent["config"]
                )
                agent_list.append(picked_agent)

    platform.hostname = hostname
    if len(platform.instances) != 0:
        platform.instances.pop(len(platform.instances) - 1)

    platform.instances.append(instance_name)
    platform.vip_address.append(vip_address)
    
    if checkbox is True:
        web_address = vip_address.replace(vip_address.split("://")[0], "http")
        platform.bind_web_address.append(web_address)
    else:
        platform.bind_web_address.append(None)

    platform.agents.append(agent_list)
    ui.open(f"http://127.0.0.1:8080/edit/{platform_name + '?update=True'}")

def change_instance(new_instance_name: str, selected_machine: str, checkbox: bool, port: int, machine_list: list, ip_list: list, table_rows: List[dict]):
    '''Saves instance that user created/edited'''
    instance = Instance(name="", vip_address="", bind_web_address=None, agents=[])
    agent_list = []
    for agent in table_rows:
        for num in range(0, 16):
            if list(AgentName)[num].value in agent['name']:
                agent["source"] = list(AgentSource)[num].value
                picked_agent = Agent(
                    name=agent["name"],
                    identity=agent["identity"],
                    source=agent["source"],
                    config=agent["config"]
                )
        agent_list.append(picked_agent)
    
    if checkbox == False:
        for index, machine in enumerate(machine_list):
            if machine == selected_machine:
                ip_address = ip_list[index]
                instance.vip_address = f"tcp://{ip_address}:22916"
    else:
        ip_address = "0.0.0.0"
        instance.vip_address = f"tcp://{ip_address}:{port}"
    
    instance.name = new_instance_name
    instance.vip_address = f"tcp://{ip_address}:22916"
    instance.bind_web_address = None
    instance.agents = agent_list

    instance.write_platform_config()
    
    instance_list = []
    for instance_dir in os.listdir(os.path.expanduser("~/.volttron_installer/platforms")):
        if os.path.isdir(os.path.expanduser(f"~/.volttron_installer/platforms/{instance_dir}")):
            print(instance_dir)
            instance_list.append(str(instance_dir))
    
    print(instance_list)
    inventory = Inventory(hosts=instance_list)
    inventory.write_inventory("inventory")
    
def remove_instance(instance_name):
    global platform
    for index, instance in enumerate(platform.instances):
        if instance == instance_name:
            platform.instances.pop(index)
            platform.vip_address.pop(index)
            platform.bind_web_address.pop(index)
            platform.agents.pop(index)
    
    if os.path.exists(os.path.expanduser("~") + f"/.volttron_installer/platforms/{platform.name}"):
        for instance_dir in os.listdir(os.path.expanduser("~") + f"/.volttron_installer/platforms/{platform.name}"):
            if os.path.isdir(os.path.expanduser("~") + f"/.volttron_installer/platforms/{platform.name}/" + instance_dir):
                if instance_name == instance_dir:
                    rmtree(os.path.expanduser("~") + f"/.volttron_installer/platforms/{platform.name}/" + instance_dir)

def remove_instance_card(caller):
    '''Display card for instance selection for removal'''
    columns = [
        {'name': 'name', 'label': 'Name', 'field': 'name', 'required': True}
    ]
    rows = []

    def handle_instance_removal(instance_name, dialog, table_dialog):
        '''Handles on_click event when user confirms the removal of a platform'''
        # Remove row where platform was being displayed
        table.remove_rows(*table.selected)
        table.selected.clear()

        remove_instance(instance_name)

        dialog.close()
        table_dialog.close()

        if caller == "edit":
            edit_page.refresh()
        elif caller == "create":
            create_page.refresh()



    def confirm_remove(instance, table_dialog):
        '''Confirmation of instance removal'''
        # Get old platform name for overriding
        instance_str = instance.replace("'", "\"")
        instance_list = json.loads(instance_str)
        instance_name = instance_list[0]['name']

        with ui.dialog() as dialog, ui.card():
            ui.label("Confirm?").style("font-size: 20px")
            ui.label(f"Are you sure you want to remove {instance_name}? This action cannot be undone.")

            with ui.row():
                ui.button("Cancel", on_click=dialog.close)
                ui.button("Confirm", on_click=lambda: handle_instance_removal(instance_name, dialog, table_dialog))

        dialog.open()
        
    for instance in platform.instances:
        rows.append({'name': instance})

    with ui.dialog() as dialog, ui.card():
        table = ui.table(title="Instances", columns=columns, rows=rows, row_key="name", selection="single")

        with ui.row():
            ui.button("Cancel", on_click=lambda: dialog.close())
            ui.button("Remove Platform", on_click=lambda: confirm_remove(label.text, dialog)).bind_visibility_from(table, "selected", backward=lambda val: bool(val))
    
        with ui.row():
            ui.label("Current Selection:")
            label = ui.label().bind_text_from(table, 'selected', lambda val: str(val))
    dialog.open()

@ui.refreshable
def edit_page(original_platform_name: str, update: str):
    '''Edit Platform; Can edit anything that was inputted (agents, configs, names, etc.)'''
    global host_list
    host_list = []

    global platform
    if update == "False":
        if instance_list == []:
            for instance_dir in os.listdir(os.path.expanduser("~") + "/.volttron_installer/platforms/" + original_platform_name):
                if os.path.isdir(os.path.expanduser("~") + "/.volttron_installer/platforms/" + original_platform_name + "/" + instance_dir):
                    instance_list.append(instance_dir)

        inventory = Inventory.read_inventory("inventory", original_platform_name) 
        platform = Platform.read_platform_config(platform.instances, original_platform_name)
        platform.hostname = inventory.hostname
    elif update == "True":
        platform = globals()['platform']

    add_header()

    ui.label("Edit Platform").style("font-size: 26px")

    ui.label("Enter the hostname of your machine.")
    hostname = ui.input(label="Hostname", placeholder=platform.hostname, value=platform.hostname, validation={'Please enter a hostname': lambda value: value.strip()})
    ui.separator()

    ui.label("Instances")
    with ui.row():
        if platform.instances == []:
            ui.label("There are currently no instances")
        else:
            for instance in platform.instances:
                ui.link(instance, f'/edit/{platform.name}/{hostname.value}/{instance + "?caller=edit"}')

        ui.button("Add Instance", on_click=lambda: add_instance(platform.name, hostname.value, platform.instances))
        ui.button("Remove Instance(s)", on_click=lambda: remove_instance_card("edit"))

    ui.separator()

@ui.refreshable
def create_page(caller: Optional[str] = None):
    '''Platform name and option to add multiple instances; Clicking "Add Instance" will open new page for configuration'''
    
    add_header()

    global platform

    ui.label("Create Instance").style("font-size: 26px")

    ui.label("Enter the hostname of your machine.")
    hostname = ui.input(label="Hostname", value="localhost")
    ui.separator()

    ui.label("Instances")
    with ui.row():
        if platform.instances == []:
            ui.label("There are currently no instances")
        else:
            for index, instance in enumerate(platform.instances):
                ui.link(instance, f'/edit/{platform.name}/{hostname.value}/{instance + "?caller=create"}')

        ui.button("Add Instance", on_click=lambda: add_instance(platform.name, hostname.value, instance_list))
        ui.button("Remove Instance(s)", on_click=lambda: remove_instance_card("create"))
    ui.separator()

# Pages; Howto still needs to be developed
@ui.page("/")
def index():
    # Check if any directories exist
    if os.path.exists(os.path.expanduser("~/.volttron_installer/platforms")):
        if os.listdir(os.path.expanduser("~/.volttron_installer/platforms")):
            home_page()
        else:
            default_home_page()
    else:
        os.makedirs(os.path.expanduser("~/.volttron_installer"))
        os.makedirs(os.path.expanduser("~/.volttron_installer/platforms"))
        default_home_page()

@ui.page("/confirm/{old_platform_name}")
def confirm(old_platform_name: str):
    if old_platform_name == "{old_platform_name}":
        confirm_platform()
    else:
        confirm_platform(old_platform_name)
    

@ui.page("/machines")
def machines():
    '''Page for adding and removing machines'''
    rows = []
    inventory = Inventory.read_inventory("inventory")
    global platform
    platform = Instance.read_platform_config(inventory.hosts)

    add_header()
    ui.label("Enter your machine name and ip address and add them to the table")
    if os.path.exists(os.path.expanduser("~/.volttron_installer/platforms/machines.yml")):
        with open(os.path.expanduser("~/.volttron_installer/platforms/machines.yml"), "r") as machines_file:
            machines_dict = safe_load(machines_file.read())

            
            for machine, ip in machines_dict['machines'].items():
                rows.append({'machine_name': str(machine), 'ip_address': str(ip['ip'])})

            table = machine_table(rows)
    else:
        table = machine_table(rows)

@ui.page("/instances")
def instances():
    rows = []
    inventory = Inventory.read_inventory("inventory")
    global platform
    platform = Instance.read_platform_config(inventory.hosts)

    add_header()
    ui.label("Add an instance by entering its name and edit an instance through the table")

    for instance in inventory.hosts:
        rows.append({'name': str(instance)})
    
    table = instance_table(rows)

@ui.page("/create")
def create(caller: Optional[str] = None):
    host_list = []
    create_page(caller)

    with ui.row():
        ui.button("Cancel", on_click=lambda: ui.open(index))
        ui.button("Install Platform", on_click=lambda: ui.open(confirm))

@ui.page("/create/{platform_name}/{hostname}/{instance_name}")
def create_host(platform_name: str, hostname: str, instance_name: str):
    agent_rows = []
    ui.label(f"Configuration of {instance_name} for {hostname}").style("font-size: 26px")
    
    ui.label("Enter the name of your instance")
    new_instance_name = ui.input(label="Instance Name", placeholder="instance", validation={'Please enter an Instance Name': lambda value: value.strip()})
    
    ui.label("Enter the vip address of the instance")
    with ui.row():
        address = ui.input(label="VIP Address", value="tcp://127.0.0.1:22916")
        web_address_checkbox = ui.checkbox("Use for Web Address (Only if web is enabled)")
    ui.separator()

    ui.label("Pick your agent and overwrite the default configuration/identity if needed")
    table = agent_table(agent_rows)

    if os.listdir(os.path.expanduser("~") + "/.volttron_installer/platforms"):
        with ui.row():
            for platform_dir in os.listdir(os.path.expanduser("~") + "/.volttron_installer/platforms/"):
                if platform_dir == platform_name:
                    ui.button("Save Instance (Edit)", on_click=lambda: save_instance_edit(platform_name, hostname, instance_name, new_instance_name.value, address.value, web_address_checkbox.value, table.rows))
                else:
                    ui.button("Save Instance", on_click=lambda: save_instance_create(platform_name, hostname, new_instance_name.value, address.value, web_address_checkbox.value, table.rows))
    else:
        with ui.row():
            ui.button("Save Instance", on_click=lambda: save_instance_create(platform_name, hostname, new_instance_name.value, address.value, web_address_checkbox.value, table.rows))


@ui.page("/edit/{instance_name}")
def edit_instance(instance_name: str):
    '''Page where users can edit instance that the user picked'''
    agent_rows = []
    machine_list = []
    ip_list = []

    if os.path.exists(os.path.expanduser(f"~/.volttron_installer/platforms/{instance_name}")):
        with open(os.path.expanduser(f"~/.volttron_installer/platforms/{instance_name}/{instance_name}.yml"), "r") as instance_config:
            instance_dict = safe_load(instance_config.read())

        for agent, config in instance_dict['agents'].items():
            with open(config['agent_config'], 'r') as config_file:
                config = safe_load(config_file.read())
            for num in range(0,16):
                if agent == list(AgentIdentity)[num].value:
                    agent_name = list(AgentName)[num].value
    
            agent_rows.append({'name': agent_name, 'identity': agent, 'config': str(config)})
    else:
        agent_rows = []
    
    with open(os.path.expanduser("~/.volttron_installer/platforms/machines.yml"), "r") as machines_config:
        machines_dict = safe_load(machines_config.read())

        for machine, ip in machines_dict['machines'].items():
            machine_list.append(machine)
            ip_list.append(ip['ip'])

    ui.label(f"Configuration of {instance_name}").style("font-size: 26px")

    ui.label("Enter the name of your instance")
    new_instance_name = ui.input(label="Instance Name", value=instance_name, validation={'Please enter a Instance Name': lambda value: value.strip()}) 
    ui.separator()

    ui.label("Pick which machine this instance will be hosted on")
    with ui.row():
        selected_machine = ui.select(machine_list, value="localhost")
        ip_checkbox = ui.checkbox("Bind to all IP's?")
    ui.separator()

    ui.label("Specify what port the instance is hosted on").bind_visibility_from(ip_checkbox, "value")
    port = ui.input("Port #", value="22916").bind_visibility_from(ip_checkbox, "value")
    ui.separator().bind_visibility_from(ip_checkbox, "value")

    ui.label("Pick your agent and overwrite the default configuration/identity if needed")
    table = agent_table(agent_rows)
        
    ui.button("Save Changes to Instance", on_click=lambda: change_instance(new_instance_name.value, selected_machine.value, ip_checkbox.value, port.value, machine_list, ip_list, table.rows))

@ui.page("/edit/{orig_platform_name}")
def edit(orig_platform_name: str, update: str):
    edit_page(orig_platform_name, update)

    with ui.row():
        ui.button("Save Platform", on_click=lambda: ui.open(f"http://127.0.0.1:8080/confirm/{orig_platform_name}"))

@ui.page("/howto")
def howto():
    add_header()

app.on_shutdown(pool.shutdown)
ui.run(title="VOLTTRON")