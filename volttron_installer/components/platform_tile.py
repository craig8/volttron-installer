"""
Module to manage Platform Tiles for a monitoring application using the Flet framework.

These objects should have the following properties:
    1. Receive real-time status updates such as health, on/off status, number of agents, any stopped agents
    2. Should route to their own unique page where additional modifications can be made
"""

from flet import *
from volttron_installer.components.agent import Agent, LocalAgent
from volttron_installer.modules.attempt_to_update_control import attempt_to_update_control
from volttron_installer.modules.dynamic_routes import dynamic_routes
from volttron_installer.modules.global_configs import global_agents
from volttron_installer.components.background import gradial_background
from volttron_installer.components.header import Header
from volttron_installer.platform_tabs import agent_config
from volttron_installer.platform_tabs.agent_config import AgentConfig
from volttron_installer.platform_tabs.platform_config import PlatformConfig
from volttron_installer.components.platform_components.platform import Platform

class PlatformTile:
    """
    Class to represent and manage a Platform Tile.

    Attributes:
        container (Container): The container that holds the platform tile.
        shared_instance (Platform): Shared instance of the Platform class containing platform information.
    """
    def __init__(self, container: Container, shared_instance: Platform) -> None:
        """
        Initialize a PlatformTile instance.
        """
        self.platform = shared_instance

        # Subscribe to platform events
        self.platform.event_bus.subscribe("update_ui", self.update_platform_tile_ui)
        self.platform.event_bus.subscribe("agent_appended", self.forward_agent_appended)
        self.platform.event_bus.subscribe("agent_removed", self.forward_agent_removed)
        self.platform.event_bus.subscribe("load_platform", self.load_agent_ui)

        self.home_container = container
        self.platform_tile = self.build_tile()

        # BUTTON FOR HEADER
        self.submit_button = OutlinedButton("Deploy Platform", disabled=True)

        # Initialize Platform Config tab
        self.platform_config_tab = PlatformConfig(
            self.platform, # passing shared instances
        ).platform_config_view()

        # Initialize Agent Config tab
        self.agent_config_tab = AgentConfig(
            self.platform,
        ).build_agent_config_tab()

        # Add route to dynamic routes dynamically
        view = self.platform_view()
        dynamic_routes[self.platform.generated_url] = view

    def load_agent_ui(self, data=None):
        """Subscribed to signal `load_platform`"""
        agents = self.platform.added_agents.keys()
        for name in agents:
            loaded_agent = LocalAgent(
                agent_name=name,
                identity=self.platform.added_agents[name]["identity"],
                agent_path=self.platform.added_agents[name]["agent_path"],
                agent_configuration=self.platform.added_agents[name]["agent_configuration"],
                config_store_entries=self.platform.added_agents[name]["config_store_entries"],
                platform=self.platform
            )
            self.platform.event_bus.publish("append_your_agent", loaded_agent)

    def forward_agent_removed(self, agent: Agent) -> None:
        agent_name: str = agent.agent_name
        del self.platform.added_agents[agent_name]
        self.platform.event_bus.publish("remove_your_agent", agent)

    def forward_agent_appended(self, agent_name: str) -> None:
        working_agent: dict = global_agents[agent_name]
        self.platform.added_agents[agent_name] = global_agents[agent_name]
        agent = LocalAgent(
            agent_name=agent_name, 
            identity=working_agent["identity"], 
            agent_path=working_agent["agent_path"], 
            agent_configuration=working_agent["agent_configuration"], 
            config_store_entries=working_agent["config_store_entries"], 
            platform=self.platform
            )
        self.platform.event_bus.publish("append_your_agent", agent)

    def get_background_color(self):
        """
        Get the background color based on platform activity.
        """
        return "#9d9d9d" if self.platform.activity == "ON" else colors.with_opacity(0.65, "#9d9d9d")

    def get_text_color(self):
        """
        Get the text color based on platform activity.
        """
        return "white" if self.platform.activity == "ON" else colors.with_opacity(0.65, "white")

    def get_status_color(self):
        """
        Get the status color based on platform activity.
        """
        return "#00ff00" if self.platform.activity == "ON" else colors.with_opacity(0.65, "#ff0000")

    def update_platform_tile_ui(self, e=None):
        """
        Update the UI components of the platform tile based on the current platform state.
        """
        # print("platformTile: updating UI...")
        # print("platformTile: I see activity is: ", self.platform.activity)
        # Update UI components based on activity state
        self.platform_tile.bgcolor = self.get_background_color()
        self.platform_tile.content.controls[0].controls[0].value = self.platform.title
        self.platform_tile.content.controls[0].controls[1].value = self.platform.activity
        self.platform_tile.content.controls[1].controls[1].value = len(self.platform.added_agents)
        for control in self.platform_tile.content.controls:
            for subcontrol in control.controls:
                if isinstance(subcontrol, Text):
                    subcontrol.color = self.get_text_color()

        # Override blanket re-styling of text
        self.platform_tile.content.controls[0].controls[1].color = self.get_status_color()

    def build_tile(self) -> Container:
        """
        Build the platform tile container.
        """
        return Container(
            width=150,
            height=150,
            border_radius=25,
            padding=padding.all(10),
            bgcolor=self.get_background_color(),
            on_click=lambda e: self.platform.page.go(self.platform.generated_url), # Routes to individualized page for managing platform
            content=Column(
                controls=[
                    Row(controls=[Text(self.platform.title, color=self.get_text_color()), Text(value=f"{self.platform.activity}", color=self.get_status_color())]),
                    Row(controls=[Text("Running Agents"), Text("0")]),
                    Row(controls=[Text("Healthy Agents"), Text("0")]),
                ]
            )
        )

    def build_card(self) -> Container:
        """
        Build the card for the platform tile.
        """
        return self.platform_tile

    def platform_view(self) -> View:
        """
        Build the view for the platform management page.
        """
        # Initializing the header and background
        header = Header(self.platform, "/").return_header()
        background_gradient = gradial_background()
        return View(
            self.platform.generated_url,
            controls=[
                Stack(
                    controls=[
                        background_gradient,
                        Column(
                            controls=[
                                header,
                                Tabs(
                                    selected_index=0,
                                    animation_duration=300,
                                    tabs=[
                                        Tab(
                                            text="Platform Config",
                                            content=self.platform_config_tab
                                        ),
                                        Tab(
                                            text="Agent Config",
                                            content=Column(
                                                controls=[    
                                                    self.agent_config_tab
                                                ],
                                                scroll=ScrollMode.ADAPTIVE,
                                            )
                                        )
                                    ],
                                    expand=1,
                                )
                            ]
                        ),
                    ],
                expand=True
                )
            ],
            padding=0
        )

# Container to hold platform tiles
platform_tile_container = Row(wrap=True)
