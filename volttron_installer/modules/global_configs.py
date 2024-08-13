"""
Example:

global agents = [
                    {       
                        'agent_name' : 'ListenerAgent' 
                        'agent_configuration' : {'key' : 'value'},
                        'default_identity' : 'Listener',
                        'agent_path' : '/path/to/identity.file',
                        'config_entry_key' : 'JSON OR CSV'
                    }
                ]

An agent name houses all the things for an agent, these dictionaries are formed and appended
global agents once an agent is properly set up
"""

global_agents = []

"""
NOTE:
When registering a platform under a host, the platform will execute their own function
appending themselves to the host, simliar to this:

global_hosts[platform_uid] = self

this will call the event listener in the platform which will tell all objects to update their ui
to the new change.
"""
global_hosts = []


def find_dict_index(lst, name):
    """
    Finds the index of the dictionary containing the specified name in a list of dictionaries.
    The name must match the value of the first item in each dictionary.

    Args:
        lst: A list of dictionaries, where each dictionary represents an item.
        name: The name to search for.

    Returns:
        The index of the dictionary containing the specified name, or None if not found.
    """
    for index, item in enumerate(lst):
        first_key = next(iter(item))
        if item[first_key] == name:
            return index
    return None
