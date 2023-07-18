from dataclasses import dataclass, field
from typing import Optional, List, Type, Dict
from urllib.parse import urlparse
from enum import Enum
from multiprocessing import Manager, Queue
from concurrent.futures import ProcessPoolExecutor

import asyncio
import json
import time

from nicegui import ui

pool = ProcessPoolExecutor()

# Create Enum's for each attribute of agent with defaults (used for easy mapping and data modification)
class AgentName(Enum):
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

source_path = "services/core/"
class AgentSource(Enum):
    SOURCE_ACTUATOR = source_path + "ActuatorAgent"
    SOURCE_BACNET = source_path + "BACnetProxy"
    SOURCE_DATAMOVER = source_path + "DataMover"
    SOURCE_DNP3 = source_path + "DNP3Agent"
    SOURCE_FORWARDHIST = source_path + "ForwardHistorian"
    SOURCE_IEEE = source_path + "IEEE2030_5Agent"
    SOURCE_MONGODB = source_path + "MongodbTaggingService"
    SOURCE_MQTTHIST = source_path + "MQTTHistorian"
    SOURCE_OPENADR = source_path + "OpenADRVenAgent"
    SOURCE_PLATFORMDRIVER = source_path + "PlatformDriverAgent"
    SOURCE_SQLAGG = source_path + "SQLAggregateHistorian"
    SOURCE_SQL = source_path + "SQLHistorian"
    SOURCE_SQLITE = source_path + "SQLiteTaggingService"
    SOURCE_VC = source_path + "VolttronCentral"
    SOURCE_VCPLATFORM = source_path + "VolttronCentralPlatform"
    SOURCE_WEATHERDOTGOV = source_path + "WeatherDotGov"

class AgentConfig(Enum):
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

# Class for agents
@dataclass
class Agent:
    name: str
    identity: str
    source: str
    config: Optional[dict] = None

# Class for platform
@dataclass
class Platform:
    name: str = "volttron"
    vip_address: Optional[str] = "tcp://127.0.0.1:22916"
    bind_web_address: Optional[str] = None
    agents: List[Agent] = field(default_factory=[])


# Create list and dicts to hold values for specific agents; used for modification of platform/frontend
agent_name_list = []
agent_identity_dict = {}
agent_config_dict = {}

for count in range(len(list(AgentName))):
    picked_agent = Agent(
        list(AgentName)[count].value,
        list(AgentIdentity)[count].value,
        list(AgentSource)[count].value,
        list(AgentConfig)[count].value
        )
    agent_name_list.append(list(AgentName)[count].value)

    agent_identity_dict[list(AgentName)[count].value] = list(AgentIdentity)[count].value
    agent_config_dict[list(AgentName)[count].value] = str(list(AgentConfig)[count].value)




'''PROGRESS BAR'''
#def install_platform(q: Queue):
#    n = 50
#    for i in range(n):
#        # Perform some heavy computation
#        time.sleep(0.1)
#
#        # Update the progress bar through the queue
#        q.put_nowait(i / n)

def setup_platform(name: str, address: str,  table: List[dict], web_address: Optional[str] = None):
    '''TRYING TO GET PROGRESS BAR TO WORK'''
    #async def start_installation():
    #    loop = asyncio.get_running_loop()
    #    
    #    await loop.run_in_executor(pool, install_platform, queue)
    #
    #queue = Manager().Queue()
    #
    #ui.timer(0.1, callback=lambda: progressbar.set_value(queue.get() if not queue.empty() else progressbar.value))
#
    #progressbar = ui.linear_progress(value=0).props('instant-feedback')
    

    # Add sources to selected agents, create objects of those agents, append those objects to a list
    agent_list = []
    count = 0
    for count in range(0, 16):
        for agent in table:
            if list(AgentName)[count].value in agent.values():
                agent["source"] = list(AgentSource)[count].value
                config = agent["config"].replace("'", "\"") # Change single quotes to double so str can be converted to dict
                picked_agent = Agent(
                    name=agent["name"],
                    identity=agent["identity"],
                    source=agent["source"],
                    config=json.loads(config) # json.loads() because config was a string for frontend display
                )
                agent_list.append(picked_agent)
        count += 1

    # Object for platform
    platform = Platform(name=name, vip_address=address, bind_web_address=web_address, agents=agent_list)
    print(platform.name)
    print(platform.vip_address)
    print(platform.bind_web_address)
    print(platform.agents)

# --------------------------------------------- WEB SIDE ---------------------------------------------
# Columns and rows for table
columns = [
    {'name': 'name', 'label': 'Name', 'field': 'name', 'sortable': True, 'required': True},
    {'name': 'identity', 'label': 'Identity', 'field': 'identity', 'required': False},
    {'name': 'config', 'label': 'Configuration', 'field': 'config', 'required': False}
]
rows = []

# Add header
def add_header():
    header_items = {
        'Home': '/',
        'Create': '/create',
        'How To': '/howto'
    }
    with ui.header():
        with ui.row():
            for title, target in header_items.items():
                ui.link(title, target).classes(replace="text-lg text-white")

# Updates the values for identity and config input based on which agent was picked
def update_choice(new_name, new_id, new_config): # Pass through objects
    # Update values on obj's
    new_id.value = agent_identity_dict[new_name.value]
    new_config.value = str(agent_config_dict[new_name.value])

    new_id.update()
    new_config.update()

def confirm_platform(platform_name, vip_address, agent_table, web_address_checkbox): # Pass through objects
    # Update values on all obj's
    platform_name.update()
    vip_address.update()
    agent_table.update()
    web_address_checkbox.update()

    # Declare web address
    web_address = vip_address.value.replace(vip_address.value.split("://")[0], "http")

    # Input web address if checkbox was clicked
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
            ui.table(title='Agents', columns=columns, rows=agent_table.rows)
        with ui.row():
            ui.button("Cancel", on_click=dialog.close)
            ui.button("Confirm", on_click=lambda: (setup_platform(platform_name.value, vip_address.value, agent_table.rows, web_address), dialog.close))
    dialog.open()        

# Table for selecting agents
def agent_table():
    ui.label("Pick your agent and overwrite the default configuration/identity if needed")
    with ui.table(title='Agents', columns=columns, rows=rows, row_key='name', selection='multiple').classes('w-75') as table:
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

# Platform name, vip-address, and table for agents; option to make vip-address bind-web-address as well
def output_data():
    add_header()
    ui.label("Create Platform").style("font-size: 26px")

    ui.label("Enter the name of the volttron platform. Leave blank for default (volttron)")
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

@ui.page("/create")
def create():
    add_header()
    platform_name_obj, vip_address_obj, agent_table_obj, checkbox = output_data()

    ui.button("Install Platform", on_click=lambda: confirm_platform(platform_name_obj, vip_address_obj, agent_table_obj, checkbox))

@ui.page("/howto")
def howto():
    add_header()
    
ui.run()