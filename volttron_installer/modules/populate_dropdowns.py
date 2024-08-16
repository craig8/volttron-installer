from flet import Dropdown, dropdown

def numerate_agent_dropdown() -> Dropdown:
    from volttron_installer.modules.global_configs import global_agents
    dropdown_options = [dropdown.Option(text=agent["agent_name"]) for agent in global_agents]
    return Dropdown(options=dropdown_options)

def numerate_host_dropdown() -> Dropdown:
    """Create a dropdown populated with the hosts that are currently registered."""
    from volttron_installer.modules.global_configs import global_hosts
    print("populate_dropdowns.py sees global_hosts as: ", global_hosts)
    dropdown_options = [dropdown.Option(text=host["host_id"]) for host in global_hosts]
    return Dropdown(options=dropdown_options)
