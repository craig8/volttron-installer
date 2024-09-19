from flet import Dropdown, dropdown
from volttron_installer.modules.global_configs import global_agents, global_drivers, global_hosts


def numerate_agent_dropdown() -> Dropdown:
    dropdown_options = [dropdown.Option(text=agent["agent_name"]) for agent in global_agents]
    return Dropdown(options=dropdown_options)

def numerate_host_dropdown() -> Dropdown:
    dropdown_options = [dropdown.Option(text=host["host_id"]) for host in global_hosts]
    return Dropdown(options=dropdown_options)

def numerate_configs_dropdown() -> Dropdown:
    print(global_drivers)
    dropdown_options = [dropdown.Option(text=driver["name"]) for driver in global_drivers]
    return Dropdown(options=dropdown_options)