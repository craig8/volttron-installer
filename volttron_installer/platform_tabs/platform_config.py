from flet import *
from volttron_installer.modules.validate_field import validate_text
from volttron_installer.components.platform_components.Platform import Platform
from volttron_installer.components.Agent import Agent


class PlatformConfig:
    def __init__(
            self,
            name_field,
            addresses_field,
            ports_field,
            submit_button,
            shared_instance: Platform,
            platform_config_agent_column,
            agent_config_column
        ) -> None:
        
        #INITIALIZE THE SHARED INSTANCE
        self.platform = shared_instance

        # Name field formation
        self.name_field = name_field
        self.name_field.value = self.platform.title  # Set the value of the name field to the title
        self.name_field.on_change = lambda e: validate_text(self.name_field, self.submit_button)
        
        # Adress field formation
        self.addresses_field = addresses_field
        self.address_field_pair = self.field_pair("Addresses", self.addresses_field)

        # Ports field formation
        self.ports_field = ports_field
        self.ports_field_pair = self.field_pair("Ports", self.ports_field)
        
        # Submit butto formation
        self.submit_button = submit_button
        self.submit_button.on_click = self.deploy_to_platform

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


        self.bus_field_pair = self.field_pair("Bus Type", Text("Zmq", size=18, color="white"))

        # GROUPING THEN FORMATION FIELDS
        self.almost_fields = [
            self.field_pair("Name", self.name_field),
            self.address_field_pair,
            self.ports_field_pair,
            self.bus_field_pair
        ]
        self.all_fields_formatted = self.divide_fields(self.almost_fields)

        self.comprehensive_view = Container(
            margin=margin.only(left=20, right=20, bottom=20, top=20),
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
                                Container(expand=2, content=Stack(controls=[Container(bottom=10, right=10, height=50, width=100, content=self.submit_button)]))
                            ]
                        )
                    )
                ]
            )
        )

    # function to clean up GUI, divides up the fieds with dividers
    def divide_fields(self, field_list) -> list:
        div = Divider(height=9, thickness=3, color="white")
        return [element for pair in zip(field_list, [div] * (len(field_list) - 1)) for element in pair] + [field_list[-1], div]

    # creat a field pair 
    def field_pair(self, field_title, input) -> Container:
        return Container(
            height=70,
            padding=padding.only(top=10, bottom=10, left=5, right=5),
            content=Row(
                controls=[
                    Container(expand=2, content=Text(f"{field_title}", size=20)),
                    Container(expand=3, content=input)
                ],
                spacing=0
            )
        )

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

    def deploy_to_platform(self, e) -> None:
        self.platform.flip_activity()
        # Tell PlatformTile to update their UI after submission
        self.platform.event_bus.publish('process_data', "self.update_platform_tile_ui()")

    def platform_config_view(self) -> Container:
        return self.comprehensive_view