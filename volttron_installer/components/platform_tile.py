"""
Module to manage Platform Tiles for a monitoring application using the Flet framework.

These objects should have the following properties:
    1. Receive real-time status updates such as health, on/off status, number of agents, any stopped agents
    2. Should route to their own unique page where additional modifications can be made
"""

from flet import *
from uvicorn import Config
from volttron_installer.modules.dynamic_routes import dynamic_routes
from volttron_installer.components.background import gradial_background
from volttron_installer.components.header import Header
from volttron_installer.platform_tabs.agent_config import AgentConfig
from volttron_installer.platform_tabs.platform_config import PlatformConfig
from volttron_installer.components.platform_components.platform import Platform
from volttron_installer.platform_tabs.config_store_manager import ConfigStoreManager

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
        self.platform.event_bus.subscribe("process_data", self.process_data)
        self.platform.event_bus.subscribe("deploy_all_data", self.process_data)
        self.platform.event_bus.subscribe("update_global_ui", self.update_global_ui)

        self.home_container = container
        self.platform_tile = self.build_tile()

        # PLATFORM CONFIG SECTION
        self.name_field = TextField(hint_text="Only letters, numbers, and underscores are allowed.")
        self.addresses_text_field = TextField(label="TCP Address")
        self.address_field = Container(content=self.addresses_text_field)
        self.ports_field = TextField(value="22916")
        self.submit_button = OutlinedButton("Deploy Platform", disabled=True)
        self.host_field = Dropdown(
            options=[
                dropdown.Option("HOSTEY")
            ]
        )

        # AGENT COLUMNS 
        self.platform_config_agent_column = Column(wrap=True, scroll=ScrollMode.AUTO)
        self.agent_config_column = Column(
            expand=3,
            scroll=ScrollMode.AUTO,
            alignment=MainAxisAlignment.START,
            controls=[]
        )

        # Initialize Platform Config tab
        self.platform_config_tab = PlatformConfig(
            self.name_field, 
            self.address_field, 
            self.ports_field, 
            self.platform, # passing shared instances
            self.platform_config_agent_column,
            self.agent_config_column
        ).platform_config_view()

        # Initialize Agent Config tab
        self.agent_config_tab = AgentConfig(
            self.platform,
            self.platform_config_agent_column,
            self.agent_config_column
        ).build_agent_config_tab()

        self.config_store_tab = ConfigStoreManager(
            self.platform.page,
            self.platform
        ).build_store_view()

        # Add route to dynamic routes dynamically
        view = self.platform_view()
        dynamic_routes[self.platform.generated_url] = view

    def update_global_ui(self):
        """
        One day this will update everything for now, its lame.
        """
        pass

    def process_data(self, data):
        """
        Process data received from subscribed events.
        """
        print("platformTile received:", data)
        eval(data)

    def submit_fields(self):
        """
        Submit and update the platform fields from the user input.
        """
        self.platform.title = self.name_field.value
        self.platform.address = self.addresses_text_field.value
        self.platform.ports = self.ports_field.value 
        self.update_platform_tile_ui()

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

    def update_platform_tile_ui(self):
        """
        Update the UI components of the platform tile based on the current platform state.
        """
        print("platformTile: updating UI...")
        print("platformTile: I see activity is: ", self.platform.activity)
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
        header = Header(self.platform, self.submit_button, "/").return_header()
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
                                                    self.agent_config_tab,
                                                    self.config_store_tab
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
