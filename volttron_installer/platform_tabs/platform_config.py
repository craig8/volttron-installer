from flet import *
from volttron_installer.components.platform_components.Platform import Platform
from volttron_installer.components.Agent import Agent
from volttron_installer.modules.field_methods import field_pair, divide_fields


class PlatformConfig:
    def __init__(
            self,
            name_field,
            addresses_field,
            ports_field,
            shared_instance: Platform,
            platform_config_agent_column,
            host_field,
            agent_config_column
        ) -> None:
        
        #INITIALIZE THE SHARED INSTANCE
        self.platform = shared_instance

        self.field_pair = field_pair
        self.divide_fields = divide_fields

        # Name field formation
        self.name_field = name_field
        self.name_field.value = self.platform.title  # Set the value of the name field to the title
        self.name_field.on_change = lambda e: self.validate_text(self.name_field)
        
        # Adress field formation
        self.addresses_field = addresses_field
        self.address_field_pair = self.field_pair("Addresses", self.addresses_field)

        # Ports field formation
        self.ports_field = ports_field
        self.ports_field_pair = self.field_pair("Ports", self.ports_field)
        

        # Agent dropdown formation
        self.agent_dropdown = self.numerate_agent_dropdown()
        self.agent_dropdown_with_button = Row(
            controls=[
                Container(expand=3, content=self.agent_dropdown),
                Container(key='DO NOT HURT ME',
                          width=40,
                          content=IconButton(icon=icons.ADD_CIRCLE_OUTLINE_ROUNDED, on_click=self.add_agent, icon_color="white"))
            ]
        )

        # COLUMNS OF DIFFERING PAGES HOLDING AGENTS  
        self.agent_config_column = agent_config_column
        self.platform_config_agent_column = platform_config_agent_column


        self.host_field = host_field
        self.host_field_pair = self.field_pair("Host", self.host_field)
        
        self.bus_field_pair = self.field_pair("Bus Type", Text("Zmq", size=18, color="white"))

        # GROUPING THEN FORMATION FIELDS
        self.almost_fields = [
            self.host_field_pair,            
            self.field_pair("Name", self.name_field),
            self.address_field_pair,
            self.ports_field_pair,
            self.bus_field_pair
        ]
        self.all_fields_formatted = self.divide_fields(self.almost_fields)

        self.comprehensive_view = Container(
            margin=margin.only(left=10, right=10, bottom=5, top=5),
            bgcolor="#20f4f4f4",
            border_radius=12,
            content=Column(
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
                        expand=True,
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

    # lowkey a repeated ahh function from modules.validate_field XDDDDD
    def validate_text(self, text_field: TextField) -> None:
        """
        Validates the text in `text_field`

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

    # grab all Agent names that were available to me 
    def numerate_agent_dropdown(self) -> Dropdown:
        from volttron_installer.modules.all_agents import agents
        dropdown_options = [dropdown.Option(text=agent) for agent in agents()]
        return Dropdown(options=dropdown_options)

    def add_agent(self, e) -> None:
        if self.agent_dropdown.value not in self.platform.added_agents:
            agent_tile_to_add = Agent(self.agent_dropdown.value, self.platform_config_agent_column,self.agent_config_column, self.platform.added_agents)
            self.platform_config_agent_column.controls.append(agent_tile_to_add.build_agent_card())
            self.platform.added_agents[self.agent_dropdown.value] = [agent_tile_to_add, False] # False because there isnt any custom JSON
            self.platform_config_agent_column.update()

            # Tell Agent Config to update their row 
            self.platform.event_bus.publish("append_agent_row", "self.append_agent_row()")

    def platform_config_view(self) -> Container:
        return self.comprehensive_view