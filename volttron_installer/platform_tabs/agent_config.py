from flet import *
from volttron_installer.components.Agent import Agent
from volttron_installer.components.platform_components.Platform import Platform

class AgentConfig:
    def __init__(self, shared_instance: Platform, platform_config_column, agent_config_column) -> None:

        # Initialize the shared isntance of Platform
        self.platform: Platform = shared_instance

        # Subscribe to event
        self.platform.event_bus.subscribe("append_agent_row", self.process_data)

        # Platform agent column and Agent config column
        self.platform_config_agent_column: Control = platform_config_column
        self.agent_config_column: Column = agent_config_column

        # Imidiately append necessary components
        self.agent_dropdown = self.numerate_agent_dropdown()
        self.agent_config_column.controls.append(self.agent_dropdown)

        self.add_agent_button =Container(key='DO NOT HURT ME',
                          width=40,
                          content=IconButton(icon=icons.ADD_CIRCLE_OUTLINE_ROUNDED, on_click=self.add_agent, icon_color="white"))
        self.agent_config_column.controls.append(self.add_agent_button)

        # Control holding a placeholder until an agent has been selected, which will
        # replace this placeholder with the agent's own configuration view
        self.configure_agent_view = Container(
            expand=3, 
            content=Container(
                    # Place holder text
                    content=Text("Select an agent to configure!")
                )
            )

        self.divider = VerticalDivider(color="white", width=9, thickness=3)
        self._comprehensive_view = Container(
            margin=margin.only(left=10, right=10, bottom=5, top=5),
            bgcolor="#20f4f4f4",
            border_radius=12,
            content=Row(
                controls=[
                    self.agent_config_column,
                    self.divider,
                    self.configure_agent_view
                ]
            )
        )

    # helper function to add agent to Agent config view
    def process_data(self, data):
        print("Agent Config received:", data)
        eval(data)

    def append_agent_row(self) -> None:
        # Grab the most recently added agent by name
        recent_agent = list(self.platform.added_agents.keys())[-1]
        agent: Agent = self.platform.added_agents[recent_agent][0]
        agent_row = agent.build_agent_row()
        self.agent_config_column.controls.append(agent_row)
        
        # Get the container that encases the row and assign it a new onclick function
        agent_row.on_click = lambda e: self.display_agent_config_menu(agent, e)

        # Update all the changes thus far
        self.agent_config_column.update()


    # Replace placeholder with the individualized agent config menu
    def display_agent_config_menu(self, agent: Agent, e) -> None:
        self.configure_agent_view.content = agent.build_agent_configuration()
        self.configure_agent_view.update()

    # Not happy with this as it is repeated code from platform_config.py
    def numerate_agent_dropdown(self) -> Dropdown:
        from volttron_installer.modules.all_agents import agents
        dropdown_options = [dropdown.Option(text=agent) for agent in agents()]
        return Dropdown(options=dropdown_options)
    
    # this too
    def add_agent(self, e) -> None:
        if self.agent_dropdown.value not in self.platform.added_agents:
            agent_tile_to_add = Agent(self.agent_dropdown.value, self.platform_config_agent_column, self.agent_config_column, self.platform.added_agents)

            # Appending to added_agents in the shared instance of Platform
            self.platform.added_agents[self.agent_dropdown.value] = [agent_tile_to_add, False] # False because agent doesn't have custom JSON yet
            
            # Handeling the platform config tab
            self.platform_config_agent_column.controls.append(agent_tile_to_add.build_agent_card())
            self.platform_config_agent_column.update()

            # Handeling the Agent Config tab
            self.append_agent_row()
            self.agent_config_column.update()

    def build_agent_config_tab(self) -> Container:
        return self._comprehensive_view