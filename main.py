from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum
from multiprocessing import Manager, Queue
from concurrent.futures import ProcessPoolExecutor
from subprocess import Popen, PIPE
from yaml import dump, safe_load

import asyncio
import os

from nicegui import app, ui

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
    config: Optional[str] = None

@dataclass
class Platform:
    '''Class for Platform and to Create Platform Configuration; Currently meant for one platform '''
    name: str = "volttron"
    vip_address: Optional[str] = "tcp://127.0.0.1:22916"
    bind_web_address: Optional[str] = None
    agents: List[Agent] = field(default_factory=[])

    def write_platform_config(self, filename: str):
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
        
        # Loop through selected agents to write their configurations
        for agent in self.agents:
            platform_dict['agents'].update({
                agent.identity: {
                    "agent_source": agent.source,
                    "agent_config": agent.config,
                    "agent_running": True,
                    "agent_enabled": True
                }
            })
        
        with open(os.path.expanduser("~") + f'/.volttron_installer/platform/{filename}/{filename}.yml', 'w') as platform_config_file:
            dump(platform_dict, platform_config_file)
        
    @staticmethod
    def read_platform_config(filename: str) -> 'Platform':
        '''Read Saved Platform Config File'''
        with open(f'{filename}.yml', 'r') as platform_config_file:
            platform_dict = safe_load(platform_config_file.read())

            return platform_dict
            
@dataclass
class Inventory:
    '''Class to Create and Read Inventory; Currently meant for one platform, will expand later'''
    hosts: List[str]

    def write_inventory(self, filename: str):
        '''Write Inventory File'''
        inventory_dict = {
            "all": {
                "hosts": {}
            }
        }

        # Add multiple hosts with their address' to the inventory dictionary; Currently meant for one platform
        for host in self.hosts:
            inventory_dict['all']['hosts'].update({host:{"ansible_host": "localhost"}}) 
        
        with open(os.path.expanduser("~") + f"/.volttron_installer/platform/{filename}.yml", 'w') as inventory_file:
            dump(inventory_dict, inventory_file)

    @staticmethod    
    def read_inventory(filename: str) -> 'Inventory':
        '''Read Saved Inventory File'''
        with open(os.path.expanduser("~") +f"/.volttron_installer/platform/{filename}.yml", 'r') as inventory_file:
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
def install_platform(q: Queue, name: str, vip_address: str,  table: List[dict], password: str, web_address: Optional[str] = None):
    '''Installs platform and updates progress bar as processes are finished'''
    platform = setup_platform(name, vip_address, table, web_address)
    q.put_nowait(20) # Update progress bar

    ## Host Configuration; handles password input; Assumes password was entered correctly
    #host_config_process = pexpect.spawn("ansible-playbook -K -i inventory.yml --connection=local volttron.deployment.host_config")
    #host_config_process.expect("BECOME password: ")
    #host_config_process.sendline(password)
#
    #host_config_process.expect(pexpect.EOF)
    #print(host_config_process.before.decode())
    #q.put_nowait(40)
#
    ## Install Platform
    #install_cmd = Popen(['bash', '-c', 'ansible-playbook -i inventory.yml --connection=local volttron.deployment.install_platform'], stdout=PIPE, stderr=PIPE)
    #stdout, stderr = install_cmd.communicate()
#
    #if stdout is not None:
    #    stdout_str = stdout.decode('utf-8')
    #    print(stdout_str)
    #if stderr is not None:
    #    stderr_str = stderr.decode('utf-8')
    #    print(stderr_str)
#
    #q.put_nowait(60)
#
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
#
    #q.put_nowait(80)
#
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
#
    #q.put_nowait(100)

# Sets up everything needed to install VOLTTRON based on what was entered 
def setup_platform(name: str, vip_address: str,  table: List[dict], web_address: Optional[str] = None) -> Platform:    
    '''Add sources to selected agents, create objects of those agents, append those objects to a list, and create config files'''
    
    # Create parent directory that any other file created will sit in for utilization; Make directories for agent configuration files and so ansible expects localhost.yml in correct location; Currently for one platform
    os.makedirs(os.path.expanduser("~") + "/.volttron_installer/platform", exist_ok=True)
    os.makedirs(os.path.expanduser("~") + "/.volttron_installer/platform/agent_configs", exist_ok=True)
    os.makedirs(os.path.expanduser("~") + f"/.volttron_installer/platform/{name}", exist_ok=True)

    agent_list = []
    num = 0
    for agent in table:
        for num in range(0, 16):
            if list(AgentName)[num].value in agent.values():
                agent["source"] = list(AgentSource)[num].value
                config = agent["config"].replace("'", "\"").replace("False", "false").replace("True", "true").replace("None", "null") # Change single quotes to double so str can be converted to dict

                # Create agent config files
                id = agent["identity"].replace(".", "_")
                with open(os.path.expanduser("~") + f'/.volttron_installer/platform/agent_configs/{id}_config', 'w') as agent_config:
                    agent_config.write(config)
                
                # Create platform object
                agent_config_path = os.path.expanduser("~") + f'.volttron_installer/platform/agent_configs/{id}_config'
                picked_agent = Agent(
                    name=agent["name"],
                    identity=agent["identity"],
                    source=agent["source"],
                    config=agent_config_path
                )
                agent_list.append(picked_agent)
            num += 1
    # Object for platform
    platform = Platform(name=name, vip_address=vip_address, bind_web_address=web_address, agents=agent_list)
    
    # Create inventory file; currently one host, will change when multiple are implemented
    inventory = Inventory([platform.name])
    inventory.write_inventory("inventory")

    # Create platform configuration file after inventory; Pass through platform (host) name to meet where volttron-ansible is expecting our platform config file
    platform.write_platform_config(platform.name)
    
    return platform

# --------------------------------------------- WEB SIDE ---------------------------------------------

# Columns and rows for agent selection table
agent_columns = [
    {'name': 'name', 'label': 'Name', 'field': 'name', 'sortable': True, 'required': True},
    {'name': 'identity', 'label': 'Identity', 'field': 'identity', 'required': False},
    {'name': 'config', 'label': 'Configuration', 'field': 'config', 'required': False}
]
agent_rows = []

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

def confirm_platform(platform_name, vip_address, table, web_address_checkbox, password): # Pass through objects
    '''Shows what the user has chosen and can be submitted'''
    # Update values on all obj's
    platform_name.update()
    vip_address.update()
    table.update()
    web_address_checkbox.update()
    password.update()

    # Declare web address
    web_address = vip_address.value.replace(vip_address.value.split("://")[0], "http")
    async def start_installation():
        '''Async event handler; Will install platform'''
        progress.visible = True
        loop = asyncio.get_running_loop()

        if web_address_checkbox.value is True:
            await loop.run_in_executor(pool, install_platform, queue, platform_name.value, vip_address.value, table.rows, password.value, web_address)
        else:
            await loop.run_in_executor(pool, install_platform, queue, platform_name.value, vip_address.value, table.rows, password.value)


    queue = Manager().Queue()

    # Output web address if checkbox was clicked
    with ui.dialog() as dialog, ui.card():
        ui.label("Overview of Selection").style("font-size: 26px")
        with ui.row():
            ui.label("Platform Name:")
            ui.label(platform_name.value)
        ui.separator()
        with ui.row():
            ui.label("VIP Address:")
            ui.label(vip_address.value)
        ui.separator()
        if web_address_checkbox.value is True:
            with ui.row():
                ui.label("Web Address:")
                ui.label(web_address)
                ui.separator()
        else:
            pass

        with ui.row():
            ui.table(title='Agents', columns=agent_columns, rows=table.rows)
        with ui.row():
            ui.button("Cancel", on_click=dialog.close)
            ui.button("Confirm", on_click=start_installation)
            progress = ui.circular_progress(min=0, max=100, value=0, size="xl").props('instant-feedback')
            progress.visible = False
            
        ui.timer(0.1, callback=lambda: progress.set_value(queue.get() if not queue.empty() else progress.value))
    dialog.open()

def agent_table():
    '''Table for selecting agents'''
    ui.label("Pick your agent and overwrite the default configuration/identity if needed")
    with ui.table(title='Agents', columns=agent_columns, rows=agent_rows, row_key='name', selection='multiple').classes('w-75') as table:
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

    # Get inventory and plaform config dictionaries from saved files
    inventory_dict = Inventory.read_inventory("inventory")
    platform_dict = Platform.read_platform_config("volttron") # Change arg later
    platform_columns = [
        {'name': 'name', 'label': 'Name', 'field': 'name', 'sortable': True},
        {'name': 'vip_address', 'label': 'VIP Address', 'field': 'address'},
        {'name': 'web_address', 'label': 'Web Address', 'field': 'address', 'required': False},
        {'name': 'num_agents', 'label': '# of Agents', 'field': 'agents'}
    ]

    platform_rows = []

def default_home_page():
    add_header()
    with ui.row():
        ui.label("There are currently no platforms installed, please")
        ui.link("Create a Platform", "/create").style('padding: none; margin: none')

def home_page():
    add_header()
    platform_table()



def create_page():
    '''Platform name, vip-address, and table for agents; option to make vip-address the bind-web-address as well'''
    add_header()
    ui.label("Create Platform").style("font-size: 26px")

    ui.label("Enter the name of the volttron platform.")
    with ui.row():
        name = ui.input(label="Platform Name", value="volttron")
    ui.separator()

    ui.label("Enter the vip address of the platform")
    with ui.row():
        address = ui.input(label="VIP Address", value="tcp://127.0.0.1:22916")
        web_address_checkbox = ui.checkbox("Use for Web Address (Only if web is enabled)")
    ui.separator()

    table = agent_table()
    return name, address, table, web_address_checkbox

# Pages; Still need to work on index (home) page and howto
@ui.page("/")
def index():
    add_header()
    if os.path.exists(os.path.expanduser("~") + '/.volttron_installer'):
        home_page()
    else:
        default_home_page()

@ui.page("/create")
def create():
    add_header()
    platform_name_obj, vip_address_obj, agent_table_obj, checkbox = create_page()

    with ui.row():
        password = ui.input(placeholder="Password", label="Password", password=True, password_toggle_button=True, validation={'Please enter your password': lambda value: value.strip()})
        ui.button("Install Platform", on_click=lambda: confirm_platform(platform_name_obj, vip_address_obj, agent_table_obj, checkbox, password))

@ui.page("/howto")
def howto():
    add_header()

app.on_shutdown(pool.shutdown)
ui.run(title="VOLTTRON")