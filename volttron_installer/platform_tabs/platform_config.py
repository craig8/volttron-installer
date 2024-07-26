from flet import *

class Agent:
    def __init__(self, agent_name, parent_container, agent_list):
        self.agent_name = agent_name
        self.parent_container = parent_container
        self.agent_list = agent_list
        self.active = False
        self.label = Text(value=self.agent_name, color=self.get_agent_color())

        # Initialize container with default agent color
        self.agent_tile = Container(
            border_radius=10,
            padding=5,
            border=border.all(4, self.get_agent_color()),
            on_hover=self.color_hover_change,
            on_click=self.remove_self,
            content=self.label,
        )

    def get_agent_color(self):
        return "red" if self.active else "green"

    def color_hover_change(self, e):
        self.active = (e.data == "true")
        new_color = self.get_agent_color()
        self.agent_tile.border = border.all(4, new_color)
        self.label.color = new_color
        self.agent_tile.update()

    def remove_self(self, e):
        if self.agent_tile in self.parent_container.controls:
            self.agent_list.remove(self.agent_name)
            self.parent_container.controls.remove(self.agent_tile)
            self.parent_container.update()

    def build_agent_card(self) -> Container:
        return self.agent_tile


class PlatformConfig:
    def __init__(self, name_field, all_addresses_checkbox, ports_field, submit_button, page: Page, platform_title: str, added_agents: list):
        self.page = page
        self.platform_title = platform_title
        self.added_agents = added_agents

        # Initialize properties for agents
        self.agent_dropdown = self.numerate_agent_dropdown()
        self.agent_dropdown_with_button = Row(
            controls=[
                Container(
                    expand=3,
                    content=self.agent_dropdown
                ),
                Container(
                    width=40,
                    content=IconButton(icon=icons.ADD_CIRCLE_OUTLINE_ROUNDED, on_click=self.add_agent, icon_color="white"),
                )
            ]
        )
        self.agent_column = Column(wrap=True, scroll=ScrollMode.AUTO)

        # Initialize platform configurations
        self.name_field = name_field
        self.name_field.value = platform_title
        self.name_field.on_change = self.validate_text
        self.name_field_pair = self.field_pair("Name", self.name_field)

        self.all_addresses_checkbox = all_addresses_checkbox
        self.address_field_pair = self.field_pair("Addresses", self.all_addresses_checkbox)

        self.ports_field = ports_field
        self.ports_field_pair = self.field_pair("Ports", self.ports_field)

        self.bus_field_pair = self.field_pair("Bus Type", Text("2mg", size=18, color="white"))

        self.almost_fields = [
            self.name_field_pair,
            self.address_field_pair,
            self.ports_field_pair,
            self.bus_field_pair
        ]

        self.all_fields_formatted=self.divide_fields(self.almost_fields) 

        self.submit_button = submit_button

        self.comprehensive_view = Container( # parent container for the cool transparent background hehee
            margin=margin.only(left=20, right=20, bottom=20, top=20),
            bgcolor="#20f4f4f4",
            border_radius=12,
            content=Column(
                alignment=MainAxisAlignment.START,
                spacing=10,  # Adjusted spacing for better separation
                controls=[
                    *self.all_fields_formatted,
                    Container(
                        #bgcolor="red",
                        height=70,
                        padding=padding.only(top=10, bottom=10, left=5, right=5),
                        content=Row(
                            expand=True,
                            controls=[
                                Container(
                                    expand=2,
                                    content=Text("Agents", size=20)
                                ),
                                Container(
                                    expand=3,
                                    content=self.agent_dropdown_with_button,
                                )
                            ]
                        )
                    ),
                    # Adding the last row ensures it is within the column structure
                    Container(
                        #bgcolor="blue",
                        expand=True,
                        content=Row(
                            spacing=0,
                            controls=[
                                Container(
                                    expand=3,
                                    #bgcolor="pink",
                                    padding=padding.only(left=4),
                                    content=self.agent_column
                                ),
                                Container(
                                    #bgcolor="orange",
                                    expand=2,
                                    content=Stack(
                                        controls=[
                                            Container(
                                                bottom=10,
                                                right=10,
                                                height=50,
                                                width=100,
                                                content=self.submit_button
                                            )
                                        ]
                                    )
                                )
                            ]
                        ),
                    )
                ]
            )
        )

    def validate_text(self, e) -> None:
        valid_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
        input_text = e.control.value
        if all(c in valid_chars for c in input_text) and 0 <= len(input_text) <= 9:
            e.control.error_text = None
            self.submit_button.disabled = False
        else:
            e.control.error_text = "Only letters, numbers, and underscores are allowed."
            self.submit_button.disabled = True
        self.submit_button.update()
        e.control.update()

    def divide_fields(self, field_list) -> list:
        div = Divider(height=9, thickness=3, color="white")
        #puts a divider in between each field pair in the field list 
        return [element for pair in zip(field_list, [div] * (len(field_list) - 1)) for element in pair] + [field_list[-1], div]
    

    def field_pair(self, text, input) -> Container:
        return Container(
            height=70,
            padding=padding.only(top=10, bottom=10, left=5, right=5),
            content=Row(
                controls=[
                    Container(
                        expand=2,
                        content=Text(f"{text}", size=20)
                    ),
                    Container(
                        expand=3,
                        content=input
                    )
                ],
                spacing=0
            )
        )

    def numerate_agent_dropdown(self) -> Dropdown:
        from volttron_installer.modules.all_agents import agents
        dropdown_options = [dropdown.Option(text=agent) for agent in agents()]
        return Dropdown(options=dropdown_options)

    def add_agent(self, e) -> None:
        if self.agent_dropdown.value and self.agent_dropdown.value not in self.added_agents:
            agent_tile_to_add = Agent(self.agent_dropdown.value, self.agent_column, self.added_agents).build_agent_card()
            self.agent_column.controls.append(agent_tile_to_add)
            self.added_agents.append(self.agent_dropdown.value)
            self.agent_column.update()
            
    def platform_config_view(self) -> Container:
        return self.comprehensive_view

