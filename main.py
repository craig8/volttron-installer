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
class Platform:
    '''Class for Platform and to Create Platform Configuration; Currently meant for one platform '''
    name: str = "volttron"
    hosts: List[str] = field(default_factory=[])
    vip_address: List[str] = "tcp://127.0.0.1:22916"
    bind_web_address: Optional[List[str]] = field(default_factory=[])
    agents: List[List[Agent]] = field(default_factory=[])

    def write_platform_config(self, hosts: List[str], platform_name: str):
        '''Write Platform Config File'''
        for index, host in enumerate(hosts):
            if self.bind_web_address[index] is not None:
                platform_dict = {
                    "config": {
                        "vip_address": self.vip_address[index],
                        "bind_web_address": self.bind_web_address[index],
                    },
                    "agents": {}
                }
            else:
                platform_dict = {
                    "config": {
                        "vip_address": self.vip_address[index],
                    },
                    "agents": {}
                }

            # Loop through selected agents to write their configurations
            for agent in self.agents[index]:
                print(agent.name)
                print(agent.identity)
                print(agent.source)
                print(agent.config)
                platform_dict['agents'].update({
                    agent.identity: {
                        "agent_source": agent.source,
                        "agent_config": agent.config,
                        "agent_running": True,
                        "agent_enabled": True
                    }
                })

            with open(os.path.expanduser("~") + f'/.volttron_installer/platforms/{platform_name}/{host}/{host}.yml', 'w') as platform_config_file:
                dump(platform_dict, platform_config_file)
    
    @staticmethod
    def read_platform_config(filename: str, platform_name: str) -> 'Platform':
        '''Read Saved Platform Config File'''
        agent_list = []
        num = 0

        with open(os.path.expanduser("~") + f'/.volttron_installer/platforms/{platform_name}/{filename}/{filename}.yml', 'r') as platform_config_file:
            platform_dict = safe_load(platform_config_file.read())
            
            # Get variables needed for a platform object; Used for frontend
            vip_address = platform_dict['config']['vip_address']
            hostname = filename
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
                    num += 1

            platform_obj = Platform(name=platform_name, hostname=hostname, vip_address=vip_address, bind_web_address=bind_web_address, agents=agent_list)   

            return platform_obj
            
@dataclass
class Inventory:
    '''Class to Create and Read Inventory; Currently meant for one platform, will expand later'''
    hosts: List[str]

    def write_inventory(self, filename: str, platform_name: str):
        '''Write Inventory File'''
        inventory_dict = {
            "all": {
                "hosts": {}
            }
        }

        # Add multiple hosts with their address' to the inventory dictionary; Currently meant for one platform
        for host in self.hosts:
            if host == "localhost":
                inventory_dict['all']['hosts'].update({
                    host: {
                        "ansible_host": "localhost",
                        "volttron_home": platform_name
                    }
                })
            else:
                inventory_dict['all']['hosts'].update({
                    host: {
                        "volttron_home": platform_name
                    }
                })
        
        with open(os.path.expanduser("~") + f"/.volttron_installer/platforms/{platform_name}/{filename}.yml", 'w') as inventory_file:
            dump(inventory_dict, inventory_file)

    @staticmethod    
    def read_inventory(filename: str, platform_name: str) -> 'Inventory':
        '''Read Saved Inventory File'''
        with open(os.path.expanduser("~") + f"/.volttron_installer/platforms/{platform_name}/{filename}.yml", 'r') as inventory_file:
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
def install_platform(q: Queue, platform: Platform, password: str):
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

def create_files(platform: Platform):    
    '''Add sources to selected agents, create objects of those agents, append those objects to a list, and create config files'''
    
    # Create parent directory that any other file created will sit in for utilization; Make directories for agent configuration files and so ansible expects localhost.yml in correct location; Currently for one platform
    os.makedirs(os.path.expanduser("~") + "/.volttron_installer/platforms", exist_ok=True)
    os.makedirs(os.path.expanduser("~") + f"/.volttron_installer/platforms/{platform.name}", exist_ok=True)

    for index, host in enumerate(platform.hosts):
        os.makedirs(os.path.expanduser("~") + f"/.volttron_installer/platforms/{platform.name}/{host}", exist_ok=True)
        os.makedirs(os.path.expanduser("~") + f"/.volttron_installer/platforms/{platform.name}/{host}/agent_configs", exist_ok=True)

        for agent in platform.agents[index]:
            for num in range(0, 16):
                if list(AgentName)[num].value == agent.name:
                    config = agent.config.replace("'", "\"").replace("False", "false").replace("True", "true").replace("None", "null") # Change single quotes to double so str can be converted to dict

                    # Create agent config files
                    id = agent.identity.replace(".", "_")
                    with open(os.path.expanduser("~") + f'/.volttron_installer/platforms/{platform.name}/{host}/agent_configs/{id}_config', 'w') as agent_config:
                        agent_config.write(config)

                    # Create platform object
                    agent_config_path = os.path.expanduser("~") + f'/.volttron_installer/platforms/{platform.name}/{host}/agent_configs/{id}_config'
                    agent.config = agent_config_path
                num += 1

    # Create inventory file
    inventory = Inventory(platform.hosts)
    inventory.write_inventory("inventory", platform.name)

    # Create platform configuration file after inventory; Pass through hostname to meet where volttron-ansible is expecting our platform config file
    platform.write_platform_config(platform.hosts, platform.name)
    
    return platform

# --------------------------------------------- WEB SIDE ---------------------------------------------

# Columns for agent tables; Constant variable
AGENT_COLUMNS = [
    {'name': 'name', 'label': 'Name', 'field': 'name', 'required': True},
    {'name': 'identity', 'label': 'Identity', 'field': 'identity', 'required': False},
    {'name': 'config', 'label': 'Configuration', 'field': 'config', 'required': False}
]

host_list = []

def add_header():
    '''Add header'''
    header_items = {
        'Home': '/',
        'Create': '/create',
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
    print(platform)

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
    
    ui.label("Hosts").style("font-size: 20px;")
    for index, host in enumerate(platform.hosts):
        rows = []
        for agent in platform.agents[index]:
            print(agent)
            rows.append({'name': agent.name, 'identity': agent.identity, 'config': str(agent.config)})

        with ui.row():
            ui.label("Hostname:")
            ui.label(host)
        ui.separator()

        with ui.row():
            ui.label("VIP Address:")
            ui.label(platform.vip_address[index])
        ui.separator()

        with ui.row():
            ui.label("Web Address:")
            ui.label(platform.bind_web_address[index])
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

def edit_page():
    '''Edit Platform; Can edit anything that was inputted (agents, configs, names, etc.); Currently meant for one platform'''
    
    # Rows for agent selection table
    agent_rows = []

    num = 0
    platforms_path = os.path.expanduser("~") + "/.volttron_installer/platforms/"
    for platform_dir in os.listdir(platforms_path):
        if os.path.isdir(platforms_path + platform_dir):
            inventory = Inventory.read_inventory("inventory", platform_dir)
            for host in range(len(inventory.hosts)):        
                platform = Platform.read_platform_config(inventory.hosts[host], platform_dir)
            
            num += 1

    # Update agent_rows so table shows correct data
    for agent in platform.agents:
        agent_rows.append({'name': agent.name, 'identity': agent.identity, 'config': str(agent.config)})

    add_header()
    # Output web address if checkbox was clicked
    ui.label("Edit Platform").style("font-size: 26px")
    with ui.row():
        ui.label("Platform Name:")
        platform_name = ui.input(label="Platform Name", value=platform.name)
    ui.separator()
    with ui.row():
        ui.label("Hostname:")
        hostname = ui.input(label="Hostname", value=platform.hostname)
    ui.separator()
    with ui.row():
        ui.label("VIP Address:")
        vip_address = ui.input(label="VIP Address", value=platform.vip_address)
        if platform.bind_web_address is None:
            web_address_checkbox = ui.checkbox("Use for Web Address (Only if web is enabled)")
        else:
            web_address_checkbox = ui.checkbox("Use for Web Address (Only if web is enabled)", value=True)
        
        ui.separator()
    
    table = agent_table(agent_rows)
                       
    return platform_name, hostname, vip_address, table, web_address_checkbox
    
def platform_table():
    '''Table to display installed platforms; Allows editing of platforms and agents'''
    platform_columns = [
        {'name': 'name', 'label': 'Name', 'field': 'name', 'sortable': True},
        {'name': 'hostname', 'label': 'Hostname', 'field': 'hostname'},
        {'name': 'vip_address', 'label': 'VIP Address', 'field': 'vip_address'},
        {'name': 'web_address', 'label': 'Web Address', 'field': 'web_address', 'required': False},
        {'name': 'num_agents', 'label': '# of Agents', 'field': 'num_agents'}
    ]

    platform_rows = []

    # Get inventory and plaform config obj's from saved files; Append info from inventory and platform config to table rows of platforms
    num = 0
    platforms_path = os.path.expanduser("~") + "/.volttron_installer/platforms/"
    for platform_dir in os.listdir(platforms_path):
        if os.path.isdir(platforms_path + platform_dir):
            inventory = Inventory.read_inventory("inventory", platform_dir)
            for host in range(len(inventory.hosts)):        
                platform = Platform.read_platform_config(inventory.hosts[host], platform_dir)
                if platform.bind_web_address == None:
                    platform_rows.append({'name': platform.name, 'hostname': platform.hostname, 'vip_address': platform.vip_address, 'web_address': 'None', 'num_agents': len(platform.agents)})
                else:
                    platform_rows.append({'name': platform.name, 'hostname': platform.hostname, 'vip_address': platform.vip_address, 'web_address': platform.bind_web_address, 'num_agents': len(platform.agents)})
            
            num += 1

    table = ui.table(title="Platforms", columns=platform_columns, rows=platform_rows, row_key="name", selection="single")
    
    return table
    
def default_home_page():
    add_header()
    with ui.row():
        ui.label("There are currently no platforms installed, please")
        ui.link("Create a Platform", "/create").style('padding: none; margin: none')

def home_page():
    add_header()
    table = platform_table()

    def open_edit_page(platform: str):
        '''Creates endpoint required for edit page and opens the edit page'''
        platform_str = platform.replace("'", "\"")
        platform_list = json.loads(platform_str)
        original_platform_name = platform_list[0]['name']
        
        ui.open(f"http://127.0.0.1:8080/edit/{original_platform_name}")

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
        
    with ui.row().bind_visibility_from(table, 'selected', backward=lambda val: bool(val)):
        ui.button('Edit', on_click=lambda: open_edit_page(label.text))
        ui.button('Remove', on_click=lambda: confirm_remove(label.text))
    
    with ui.row():
        ui.label("Current Selection:")
        label = ui.label().bind_text_from(table, 'selected', lambda val: str(val))


def add_host(platform_name: str, host_list: list):
    '''Adds host to host list and opens configuration page for that host'''
    if host_list == []:
        hostname = "host1"
        host_list.append(hostname)
        ui.open(f"http://127.0.0.1:8080/create/{platform_name}/{hostname}")
    else:    
        hostname = f"host{len(host_list) + 1}"
        host_list.append(hostname)
        ui.open(f"http://127.0.0.1:8080/create/{platform_name}/{hostname}")

# Make a global platform obj that will be used so each host can append configurations to the overall platform
platform = Platform(name="", hosts=[], vip_address=[], bind_web_address=[], agents=[])
def save_host(platform_name: str, hostname: str, vip_address: str, checkbox: bool, table_rows: List[dict]):
    '''Save host configuration and append values to an object'''
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
    platform.hosts.append(hostname)
    platform.vip_address.append(vip_address)
    if checkbox is True:
        web_address = vip_address.replace(vip_address.split("://")[0], "http")
        platform.bind_web_address.append(web_address)
    else:
        platform.bind_web_address.append(None)

    platform.agents.append(agent_list)
    ui.open(create)

def save_host_edit(host: str, platform_name: str, new_hostname: str, vip_address: str, checkbox_value: bool, table_rows: List[dict]):
    for index, hostname in enumerate(platform.hosts):
        if hostname == host:
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
            
            # Update values
            platform.name = platform_name
            platform.hosts[index] = new_hostname
            platform.vip_address[index] = vip_address

            if checkbox_value is True:
                web_address = vip_address.replace(vip_address.split("://")[0], "http")
                platform.bind_web_address[index] = web_address
            else:
                web_address = None
                platform.bind_web_address[index] = web_address
            
            platform.agents[index] = agent_list
        
    print(platform)
        
    ui.open(create)

def create_page():
    '''Platform name and option to add multiple hosts; Clicking "Add Host" will open new page for configuration'''
    
    ui.label("Create Platform").style("font-size: 26px")

    ui.label("Enter the name of the volttron platform.")
    platform_name = ui.input(label="Platform Name", value="volttron1")
    ui.separator()

    ui.label("Hosts")
    with ui.row():
        if platform.hosts == []:
            ui.label("There are currently no hosts")
        else:
            for host in platform.hosts:
                ui.link(host, f'/edit/{platform_name.value}/{host}')

        ui.button("Add Host", on_click=lambda: add_host(platform_name.value, host_list))
    ui.separator()

# Pages; Howto still needs to be developed
@ui.page("/")
def index():
    # Check if any directories exist
    if os.listdir(os.path.expanduser("~") + "/.volttron_installer/platforms"):
        home_page()
    else:
        default_home_page()

@ui.page("/confirm/{old_platform_name}")
def confirm(old_platform_name: Optional[str] = None):
    if old_platform_name == "{old_platform_name}":
        confirm_platform()

@ui.page("/create")
def create():
    create_page()

    with ui.row():
        ui.button("Cancel", on_click=lambda: ui.open(index))
        ui.button("Install Platform", on_click=lambda: ui.open(confirm))


@ui.page("/create/{platform_name}/{hostname}")
def create_host(platform_name: str, hostname: str):
    agent_rows = []
    ui.label(f"Configuration for {hostname} for {platform_name}").style("font-size: 26px")
    
    ui.label("Enter the hostname of your host machine")
    new_hostname = ui.input(label="Hostname", placeholder="localhost", validation={'Please enter a hostname': lambda value: value.strip()})
    
    ui.label("Enter the vip address of the host")
    with ui.row():
        address = ui.input(label="VIP Address", value="tcp://127.0.0.1:22916")
        web_address_checkbox = ui.checkbox("Use for Web Address (Only if web is enabled)")
    ui.separator()

    ui.label("Pick your agent and overwrite the default configuration/identity if needed")
    table = agent_table(agent_rows)

    with ui.row():
        ui.button("Save Host", on_click=lambda: save_host(platform_name, new_hostname.value, address.value, web_address_checkbox.value, table.rows))

@ui.page("/edit/{platform_name}/{hostname}")
def edit_host(platform_name: str, hostname: str):
    for index, host in enumerate(platform.hosts):
        if host == hostname:
            agent_rows = []
            ui.label(f"Configuration for {hostname} for {platform_name}").style("font-size: 26px")

            ui.label("Enter the hostname of your host machine")
            new_hostname = ui.input(label="Hostname", value=host, validation={'Please enter a hostname': lambda value: value.strip()})

            ui.label("Enter the vip address of the host")
            if platform.bind_web_address[index] is None:
                with ui.row():
                    address = ui.input(label="VIP Address", value=platform.vip_address[index])
                    web_address_checkbox = ui.checkbox("Use for Web Address (Only if web is enabled)", value=False)
                ui.separator()
            else:
                with ui.row():
                    address = ui.input(label="VIP Address", value=platform.vip_address[index])
                    web_address_checkbox = ui.checkbox("Use for Web Address (Only if web is enabled)", value=True)
                ui.separator()

            for agent in platform.agents[index]:
                agent_rows.append({'name': agent.name, 'identity': agent.identity, 'config': str(agent.config)})

            ui.label("Pick your agent and overwrite the default configuration/identity if needed")
            table = agent_table(agent_rows)

            ui.button("Save Changes to Host", on_click=lambda: save_host_edit(host, platform_name, new_hostname.value, address.value, web_address_checkbox.value, table.rows))

@ui.page("/edit/{orig_platform_name}")
def edit(orig_platform_name):
    add_header()
    platform_name_obj, hostname_obj, vip_address_obj, agent_table_obj, checkbox = edit_page()

    with ui.row():
        ui.button("Save Platform", on_click=lambda: confirm_platform("Save Configuration", platform_name_obj, hostname_obj, vip_address_obj, agent_table_obj, checkbox, orig_platform_name))

@ui.page("/howto")
def howto():
    add_header()

app.on_shutdown(pool.shutdown)
ui.run(title="VOLTTRON")