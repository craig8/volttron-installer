"""
Example:

global agents = {
                'agent_name' : {
                        'agent_configuration' : 'JSON/CSV',
                        'default_identity' : 'whatever',
                        'agent_path' : r'string',
                        'config_entry_key' : 'JSON OR CSV'
                    },
                }

An agent name houses all the things for an agent, these dictionaries are formed and appended
global agents once an agent is properly set up
"""

global_agents = {}

"""
NOTE:
When registering a platform under a host, the platform will execute their own function
appending themselves to the host, simliar to this:

global_hosts[platform_uid] = self

this will call the event listener in the platform which will tell all objects to update their ui
to the new change.
"""
global_hosts = {} 