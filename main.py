from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from enum import Enum
from multiprocessing import Manager, Queue
from nicegui import app, ui
from shutil import rmtree
from subprocess import PIPE, Popen
from typing import List, Optional
from urllib.parse import urlparse
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
    def read_platform_config(instance: str) -> 'Instance':
        '''Read Saved Platform Config File'''
        machine_list = []
        ip_list = []
        instance_obj = Instance(name="", vip_address="", bind_web_address="", agents=[])
        
        with open(os.path.expanduser("~/.volttron_installer/platforms/machines.yml"), 'r') as machines_config:
            machines_dict = safe_load(machines_config.read())

            for machine, ip in machines_dict['machines'].items():
                machine_list.append(machine)
                ip_list.append(ip['ip'])

        agent_list = []
        with open(os.path.expanduser("~") + f'/.volttron_installer/platforms/{instance}/{instance}.yml', 'r') as platform_config_file:
            platform_dict = safe_load(platform_config_file.read())

        # Get variables needed for the platform object; Used for frontend
        if 'vip_address' in platform_dict['config']:
            vip_address = platform_dict['config']['vip_address']
        else:
            vip_address = None

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
        instance_obj.agents = agent_list

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
def install_platform(q: Queue, instance_list: List[Instance], password: str):
    '''Installs platform and updates progress bar as processes are finished'''
    for instance in instance_list:
        print(instance)
    create_files(instance_list)
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

def create_files(instance_list: List[Instance]):    
    '''Create temporary inventory file that will serve as the inventory when a machine is deployed'''
    global_inventory = Inventory.read_inventory("inventory")
    
    inventory_dict = {
        "all": {
            "hosts": {}
        }
    }

    for instance in instance_list:
        if instance.name in global_inventory.hosts:
            with open(os.path.expanduser("~/.volttron_installer/platforms/inventory.yml"), 'r') as inventory_file:
                global_inventory_dict = safe_load(inventory_file.read())
                print(global_inventory_dict)
            volttron_home = global_inventory_dict['all']['hosts'][f'{instance.name}']['volttron_home']

            inventory_dict['all']['hosts'].update({
                instance.name: {
                    "volttron_home": volttron_home
                }
            })

    with open(os.path.expanduser("~") + f"/.volttron_installer/platforms/temp_inventory.yml", 'w') as inventory_file:
            dump(inventory_dict, inventory_file)


# --------------------------------------------- WEB SIDE ---------------------------------------------

# Columns for agent tables; Constant variable
AGENT_COLUMNS = [
    {'name': 'name', 'label': 'Name', 'field': 'name', 'required': True},
    {'name': 'identity', 'label': 'Identity', 'field': 'identity', 'required': False},
    {'name': 'config', 'label': 'Configuration', 'field': 'config', 'required': False}
]

def add_header(page_name: str):
    '''Add header'''
    header_items = {
        'Home': '/',
        'Machines': '/machines',
        'Instances': '/instances'
    }

    with ui.header():
        with ui.row():
            for title, target in header_items.items():
                if title == page_name:
                    ui.link(title, target).style("color: white; text-decoration: none; font-size: 16px; font-weight: bold")
                else:
                    ui.link(title, target).style("color: white; text-decoration: none; font-size: 16px")


def update_choice(new_name, new_id, new_config): # Pass through objects
    '''Updates the values for identity and config input based on which agent was picked'''
    new_id.value = agent_identity_dict[new_name.value]
    new_config.value = str(agent_config_dict[new_name.value])

    new_id.update()
    new_config.update()

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
    
def platform_table(rows: List[dict]):
    '''Table to display installed machines/instances'''
    platform_columns = [
        {'name': 'machine_name', 'label': 'Machine', 'field': 'machine_name', 'sortable': True},
        {'name': 'instances', 'label': 'Instance(s)', 'field': 'instances'},
    ]

    def open_confirm_page(label: str):
        '''Creates endpoint required for confirm page and opens confirm page'''
        label_str = label.replace("'", "\"")
        label_list = json.loads(label_str)
        machine_name = label_list[0]['machine_name']

        ui.open(f"http://127.0.0.1:8080/confirm/{machine_name}")

    table = ui.table(title="Platforms", columns=platform_columns, rows=rows, row_key="machine_name", selection="single")
    
    ui.button("Deploy Machine", on_click=lambda: open_confirm_page(label.text)).bind_visibility_from(table, 'selected', backward=lambda val: bool(val))
    
    with ui.row().bind_visibility_from(table, 'selected', backward=lambda val: bool(val)):
        ui.label("Current Selection:")
        label = ui.label().bind_text_from(table, 'selected', lambda val: str(val))

    return table

def machine_table(rows):
    '''Table to display existing machines; Allows for removal of machines'''
    machine_columns = [
        {'name': 'name', 'label': 'Machine Name', 'field': 'name', 'sortable': True},
        {'name': 'ip_address', 'label': 'IP Address', 'field': 'ip_address', 'sortable': True},
        #{'name': 'date_created', 'label': 'Date Created', 'field': 'date_created'}
    ]

    def remove_machine(machine: str):
        '''Remove machine from inventory'''
        machine_str = machine.replace("'", "\"")
        machine_list = json.loads(machine_str)
        machine_name = machine_list[0]['name']
        machine_ip = machine_list[0]['ip_address']

        with open(os.path.expanduser("~/.volttron_installer/platforms/machines.yml"), 'r') as machines_file:
            machines_dict = safe_load(machines_file.read())

        for instance_dir in os.listdir(os.path.expanduser("~/.volttron_installer/platforms")):
            if os.path.isdir(os.path.expanduser(f"~/.volttron_installer/platforms/{instance_dir}")):
                with open(os.path.expanduser(f"~/.volttron_installer/platforms/{instance_dir}/{instance_dir}.yml"), 'r') as instance_file:
                    instance_dict = safe_load(instance_file.read())

                    if 'vip_address' in instance_dict['config']:
                        parsed_url = urlparse(instance_dict['config']['vip_address'])
                        ip = parsed_url.hostname

                        if ip == machine_ip:
                            del instance_dict['config']['vip_address']
                
                with open(os.path.expanduser(f"~/.volttron_installer/platforms/{instance_dir}/{instance_dir}.yml"), 'w') as instance_file:
                    dump(instance_dict, instance_file)

        del machines_dict['machines'][f'{machine_name}']
        
        with open(os.path.expanduser("~/.volttron_installer/platforms/machines.yml"), 'w') as machines_file:
            dump(machines_dict, machines_file)
        
        table.remove_rows(*table.selected)
        table.selected.clear()

    def add_machine(name: str, ip: str):
        '''Add machine to inventory'''
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

    table = ui.table(title='Host Machines', columns=machine_columns, rows=rows, row_key='name', selection='single').classes('w-75')
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

    with ui.row().bind_visibility_from(table, 'selected', backward=lambda val: bool(val)):
        ui.button('Remove', on_click=lambda: remove_machine(label.text))
    
    with ui.row():
        ui.label("Current Selection:")
        label = ui.label().bind_text_from(table, 'selected', lambda val: str(val))
    
    return table

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

        ui.open(f"http://127.0.0.1:8080/edit/{original_instance_name}")
    
    def add_instance(instance_name: str):
        instance = Instance(name=instance_name, vip_address="", bind_web_address="", agents=[])
        instance.write_platform_config()

    def remove_instance(instance: str):
        '''Removes all files related to instance and removes instance from inventory'''
        instance_str = instance.replace("'", "\"")
        instance_list = json.loads(instance_str)
        instance_name = instance_list[0]['name']

        with open(os.path.expanduser("~") + "/.volttron_installer/platforms/inventory.yml", 'r') as inventory_file:
            inventory_dict = safe_load(inventory_file.read())

            del inventory_dict['all']['hosts'][f'{instance_name}']
        
        with open(os.path.expanduser("~") + "/.volttron_installer/platforms/inventory.yml", 'w') as inventory_file:
            dump(inventory_dict, inventory_file)

        rmtree(os.path.expanduser("~") + f"/.volttron_installer/platforms/{instance_name}")

        table.remove_rows(*table.selected)
        table.selected.clear()

    with ui.table(title='Instances', columns=instance_columns, rows=rows, row_key='name', selection='single').classes('w-75') as table:
        with table.add_slot('header'):
            with table.row():
                with table.cell():
                    ui.button(on_click=lambda: (
                        table.add_rows({'name': str(new_name.value)}),
                        add_instance(new_name.value),
                        new_name.set_value(""),
                        table.update()
                    ), icon='add').props('flat fab-mini')
                with table.cell():
                    new_name = ui.input(label="Instance Name")

    with ui.row().bind_visibility_from(table, 'selected', backward=lambda val: bool(val)):
        ui.button('Edit', on_click=lambda: open_instance_page(label.text))
        ui.button('Remove', on_click=lambda: remove_instance(label.text))
    
    with ui.row():
        ui.label("Current Selection:")
        label = ui.label().bind_text_from(table, 'selected', lambda val: str(val))
    
    return table

def default_home_page():
    '''Default home page; called when no instances/machines exist'''
    add_header("Home")
    with ui.row():
        ui.label("There are no host machines added or instances installed.")
        ui.button("Add a Host Machine", on_click=lambda: ui.open("http://127.0.0.1:8080/machines"))

def home_page():
    '''Home Page; called when instances/machines do exist'''
    add_header("Home")        

    platform_rows = []
    machine_list = []
    ip_list = []

    # Create and append table rows from inventory and platform config files
    platforms_path = os.path.expanduser("~") + "/.volttron_installer/platforms/"
    inventory = Inventory.read_inventory("inventory")

    with open(os.path.expanduser("~/.volttron_installer/platforms/machines.yml"), 'r') as machines_config:
            machines_dict = safe_load(machines_config.read())

            for machine, ip in machines_dict['machines'].items():
                machine_list.append(machine)
                ip_list.append(ip['ip'])
                
    for index, machine in enumerate(machine_list):
        instance_list = []
        for instance in inventory.hosts:
            if os.path.isdir(platforms_path + instance):
                platform = Instance.read_platform_config(instance)

                parsed_url = urlparse(platform.vip_address)
                ip_address = parsed_url.hostname

                if ip_address == ip_list[index] or ip_address == "0.0.0.0":
                    instance_list.append(platform.name)
                
        instances = ', '.join(instance_list)
        platform_rows.append({'machine_name': machine, 'instances': instances})

    ui.label("Deploy a machine by selecting one below or Add a Machine/Instance")
    with ui.row():
        ui.button("Add Machine", on_click=lambda: ui.open("http://127.0.0.1:8080/machines"))
        ui.button("Add Instance", on_click=lambda: ui.open("http://127.0.0.1:8080/instances"))

    table = platform_table(platform_rows)
    

def change_instance(old_instance_name: str, new_instance_name: str, selected_machine: str, checkbox: bool, port: int, machine_list: list, ip_list: list, table_rows: List[dict]):
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
                instance.vip_address = f"tcp://{ip_address}:{port}"
    else:
        ip_address = "0.0.0.0"
        instance.vip_address = f"tcp://{ip_address}:{port}"
    
    instance.name = new_instance_name
    instance.bind_web_address = None
    instance.agents = agent_list

    if new_instance_name != old_instance_name:
        rmtree(os.path.expanduser(f"~/.volttron_installer/platforms/{old_instance_name}"))

    instance.write_platform_config()
    
    instance_list = []
    for instance_dir in os.listdir(os.path.expanduser("~/.volttron_installer/platforms")):
        if os.path.isdir(os.path.expanduser(f"~/.volttron_installer/platforms/{instance_dir}")):
            instance_list.append(str(instance_dir))
    
    inventory = Inventory(hosts=instance_list)
    inventory.write_inventory("inventory")

    ui.open("http://127.0.0.1:8080/instances")

def confirm_platform(machine_name: str):
    '''Page that will show selected machine/instances; can be either one machine or all machines. Can be submitted for installation of those instances'''
    instance_list = []

    
    with open(os.path.expanduser("~/.volttron_installer/platforms/machines.yml"), 'r') as machines_file:
        machines_dict = safe_load(machines_file.read())

    for instance_dir in os.listdir(os.path.expanduser("~/.volttron_installer/platforms")):
        if os.path.isdir(os.path.expanduser(f"~/.volttron_installer/platforms/{instance_dir}")):
            with open(os.path.expanduser(f"~/.volttron_installer/platforms/{instance_dir}/{instance_dir}.yml"), 'r') as instance_file:
                instance_dict = safe_load(instance_file.read())

                if 'vip_address' in instance_dict['config']:
                    parsed_url = urlparse(instance_dict['config']['vip_address'])
                    ip = parsed_url.hostname

                    if ip == machines_dict['machines'][f'{machine_name}']['ip']:
                        instance = Instance.read_platform_config(instance_dir)
                        instance_list.append(instance)
                    elif ip == "0.0.0.0.":
                        instance = Instance.read_platform_config(instance_dir)
                        instance_list.append(instance)
                    
    async def start_installation():
        '''Async event handler; Will install platform'''
        progress.visible = True
        loop = asyncio.get_running_loop()
 
        await loop.run_in_executor(pool, install_platform, queue, instance_list, password.value)
 
    queue = Manager().Queue()

    # Output web address if checkbox was clicked
    ui.label("Overview of Configuration").style("font-size: 26px")
    with ui.row():
        ui.label("Machine Name:")
        ui.label(machine_name)
    ui.separator()

    with ui.row():
        ui.label("IP Address:")
        ui.label(machines_dict['machines'][f'{machine_name}']['ip'])
    ui.separator()
    
    ui.label("Instances").style("font-size: 20px;")
    for instance in instance_list:
        rows = []
        for agent in instance.agents:
            rows.append({'name': agent.name, 'identity': agent.identity, 'config': str(agent.config)})

        with ui.row():
            ui.label("Instance Name:")
            ui.label(instance.name)
        ui.separator()

        with ui.row():
            ui.label("VIP Address:")
            ui.label(instance.vip_address)
        ui.separator()

        with ui.row():
            ui.label("Web Address:")
            ui.label(str(instance.bind_web_address))
        ui.separator()

        with ui.row():
            ui.table(title='Agents', columns=AGENT_COLUMNS, rows=rows)
        ui.separator()
        
    ui.label("Enter your password then click 'Confirm' to start the installation process")
    with ui.row():
        password = ui.input(placeholder="Password", label="Password", password=True, password_toggle_button=True, validation={'Please enter your password': lambda value: value.strip()})
        ui.button("Cancel", on_click=lambda: ui.open(index))
        ui.button("Confirm", on_click=start_installation)
        progress = ui.circular_progress(min=0, max=100, value=0, size="xl").props('instant-feedback')
        progress.visible = False
        
    ui.timer(0.1, callback=lambda: progress.set_value(queue.get() if not queue.empty() else progress.value))
# Pages; Howto still needs to be developed
@ui.page("/")
def index():
    '''Checks for existing existing instances/machines and redirects to appropriate home page'''
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
    
@ui.page("/machines")
def machines():
    '''Page for adding and removing machines'''
    rows = []
    if os.path.exists(os.path.expanduser("~/.volttron_installer/platforms/machines.yml")):
        with open(os.path.expanduser("~/.volttron_installer/platforms/machines.yml"), "r") as machines_file:
            machines_dict = safe_load(machines_file.read())

            for machine, ip in machines_dict['machines'].items():
                rows.append({'name': str(machine), 'ip_address': str(ip['ip'])})

    add_header("Machines")
    ui.label("Enter your machine name and ip address and add them to the table")
    table = machine_table(rows)

@ui.page("/instances")
def instances():
    '''Page for instance display'''
    rows = []

    # Create rows for instance table 
    if os.path.exists(os.path.expanduser("~/.volttron_installer/platforms/inventory.yml")):
        inventory = Inventory.read_inventory("inventory")

        for instance in inventory.hosts:
            rows.append({'name': str(instance)})

    add_header("Instances")
    ui.label("Add an instance by entering its name and edit an instance through the table")
    table = instance_table(rows)

@ui.page("/edit/{instance_name}")
def edit_instance(instance_name: str):
    '''Page where users can edit instance that the user picked'''
    agent_rows = []
    machine_list = []
    ip_list = []

    # Get machine info about instance for correct data display
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
        if 'vip_address' in instance_dict['config']:
            vip_address = instance_dict['config']['vip_address']

            parsed_url = urlparse(vip_address)
            ip_address = parsed_url.hostname
        else:
            ip_address = None
    else:
        agent_rows = []
        ip_address = None
    
    with open(os.path.expanduser("~/.volttron_installer/platforms/machines.yml"), "r") as machines_config:
        machines_dict = safe_load(machines_config.read())

        for machine, ip in machines_dict['machines'].items():
            machine_list.append(machine)
            ip_list.append(ip['ip'])

    ui.label(f"Configuration of {instance_name}").style("font-size: 26px")

    ui.label("Enter the name of your instance")
    new_instance_name = ui.input(label="Instance Name", value=instance_name, validation={'Please enter a Instance Name': lambda value: value.strip()}) 
    ui.separator()

    if ip_address is not None:
        for index, ip in enumerate(ip_list):
            if ip == ip_address:
                machine = machine_list[index]

    ui.label("Pick which machine and port this instance will be hosted on")
    with ui.row():
        if ip_address is None:
            selected_machine = ui.select(machine_list, value=machine_list[0])
            port = ui.input("Port #", value="22916")
        else:
            selected_machine = ui.select(machine_list, value=machine)
            port = ui.input("Port #", value="22916")


        ip_checkbox = ui.checkbox("Bind to all IP's?")
    ui.separator()

    ui.label("Pick your agent and overwrite the default configuration/identity if needed")
    table = agent_table(agent_rows)
        
    ui.button("Save Changes to Instance", on_click=lambda: change_instance(instance_name, new_instance_name.value, selected_machine.value, ip_checkbox.value, port.value, machine_list, ip_list, table.rows))

@ui.page("/confirm/{machine_name}")
def confirm(machine_name: str):
    confirm_platform(machine_name)

app.on_shutdown(pool.shutdown)
ui.run(title="VOLTTRON")