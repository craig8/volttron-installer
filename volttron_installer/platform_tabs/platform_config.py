"""
Module to manage the platform configuration in a platform management application using the Flet framework.
"""

from flet import *
from volttron_installer.components.platform_components.platform import Platform
from volttron_installer.components.agent import Agent
from volttron_installer.modules.create_field_methods import field_pair, divide_fields
from volttron_installer.modules.global_configs import global_agents, global_hosts
from volttron_installer.modules.populate_dropdowns import numerate_host_dropdown, numerate_agent_dropdown


class PlatformConfig:
    """
    Class to represent and manage the platform configuration.

    Attributes:
        name_field (TextField): The text field for the platform name.
        addresses_field (TextField): The text field for platform addresses.
        ports_field (TextField): The text field for platform ports.
        shared_instance (Platform): Shared instance of the Platform class containing platform information.
        platform_config_agent_column (Column): Column to hold the platform configuration agents.
        agent_config_column (Column): Column to hold the agent configuration.

        HEADS UP THESE ARE ALL USELESS WE ONLY NEEDED TO PASS THE ``shared_instance`` AND ``agent_config_column``
        BECAUSE WE CAN JUST ASSIGN OUR OWN TEXT FIELDS ANS SUCH
    """
    def __init__(self,
                 shared_instance: Platform,
                 platform_config_agent_column,
                 agent_config_column) -> None:
        """
        Initialize a PlatformConfig instance.

        Args:
            name_field (TextField): Text field for the platform name.
            addresses_field (TextField): Text field for the platform addresses.
            ports_field (TextField): Text field for the platform ports.
            shared_instance (Platform): Shared instance of the Platform class.
            platform_config_agent_column (Column): Column to hold the platform configuration agents.
            agent_config_column (Column): Column to hold the agent configuration.
        """
        # Initialize the shared instance
        self.platform = shared_instance
        self.platform.event_bus.subscribe("update_global_ui", self.update_platform_config_ui)

        # Name field initialization
        self.name_field = TextField(hint_text="Only letters, numbers, and underscores are allowed.")
        self.name_field.value = self.platform.title  # Set the value of the name field to the platform title
        self.name_field.on_change = lambda e: self.validate_text(self.name_field)
        
        # Address field initialization
        self.addresses_text_field = TextField(label="TCP Address")
        self.address_field_pair = field_pair("Addresses", self.addresses_text_field)

        # Ports field initialization
        self.ports_field = TextField(value="22916")
        self.ports_field_pair = field_pair("Ports", self.ports_field)
        
        # Agent dropdown initialization
        self.agent_dropdown = numerate_agent_dropdown()
        self.agent_dropdown_with_button = Row(
            controls=[
                Container(expand=3, content=self.agent_dropdown),
                Container(key='DO NOT HURT ME',
                          width=40,
                          content=IconButton(icon=icons.ADD_CIRCLE_OUTLINE_ROUNDED, on_click=self.add_agent, icon_color="white"))
            ]
        )

        # Columns of differing pages holding agents  
        self.agent_config_column = agent_config_column
        self.platform_config_agent_column = platform_config_agent_column

        # Host field initialization
        self.host_field = numerate_host_dropdown()
        self.host_field_pair = field_pair("Host", self.host_field)
        
        self.bus_field_pair = field_pair("Bus Type", Text("Zmq", size=18, color="white"))

        # Grouping fields for display
        self.almost_fields = [
            self.host_field_pair,
            field_pair("Name", self.name_field),
            self.address_field_pair,
            self.ports_field_pair,
            self.bus_field_pair
        ]
        self.all_fields_formatted = divide_fields(self.almost_fields)

        self.comprehensive_view = Container(
            margin=margin.only(left=10, right=10, bottom=5, top=5),
            bgcolor="#20f4f4f4",
            border_radius=12,
            content=Column(
                scroll=ScrollMode.AUTO,
                alignment=MainAxisAlignment.START,
                spacing=10,  # Adjusted spacing for better separation
                controls=[
                    *self.all_fields_formatted,
                    Container(
                        height=70,
                        padding=padding.only(top=10, bottom=10, left=5, right=5),
                        content=Row(
                            expand=True,
                            controls=[
                                Container(expand=2, content=Text("Agents", size=20)),
                                Container(expand=3, content=self.agent_dropdown_with_button)
                            ]
                        )
                    ),
                    Container(
                        content=Row(
                            spacing=0,
                            controls=[
                                Container(expand=3, padding=padding.only(left=4), content=self.platform_config_agent_column),
                            ]
                        )
                    )
                ]
            )
        )
    def update_platform_config_ui(self, data=None):
        self.update_host_dropdown()
    
    def update_host_dropdown(self):
        new_host_field = numerate_host_dropdown()
        self.host_field_pair.content.controls[1].content = new_host_field  # Update the host field with new host values
        self.host_field = new_host_field

    def validate_text(self, text_field: TextField) -> None:
        """
        Validate the text in `text_field`.

        Args:
            text_field (TextField): The text field to validate.
        """
        valid_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
        input_text = text_field.value
        if all(c in valid_chars for c in input_text):
            text_field.error_text = None
            self.platform.event_bus.publish("deploy_button_update", False)
        else:
            text_field.error_text = "Only letters, numbers, and underscores are allowed."
            self.platform.event_bus.publish("deploy_button_update", True)
        text_field.update()

    def add_agent(self, e) -> None:
        """
        Add an agent to the platform configuration.

        Args:
            e: The event object.
        """
        if self.agent_dropdown.value not in self.platform.added_agents:
            agent_tile_to_add = Agent(self.agent_dropdown.value, self.platform_config_agent_column, self.agent_config_column, self.platform.added_agents)
            self.platform_config_agent_column.controls.append(agent_tile_to_add.build_agent_card())
            self.platform.added_agents[self.agent_dropdown.value] = [agent_tile_to_add, False]  # False because there isn't any custom JSON
            self.platform_config_agent_column.update()

            # Tell Agent Config to update their row 
            self.platform.event_bus.publish("append_agent_row", "self.append_agent_row()")

    def platform_config_view(self) -> Container:
        """
        Return the comprehensive view container for the platform configuration.

        Returns:
            Container: The comprehensive view container.
        """
        return self.comprehensive_view
