from flet import *
from volttron_installer.components.program_card import ProgramTile

class Agent:
    def __init__(self, agent_name, parent_container, agent_list):
        self.agent_name = agent_name
        self.parent_container = parent_container  # Reference to the parent container (column)
        self.agent_list = agent_list
        self.active = False  # Initial hover state

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
        # Return color based on active state and initialize default colors
        return "red" if self.active else "green"

    def color_hover_change(self, e):
        # Update active state based on hover
        self.active = (e.data == "true")

        # Update the color based on the new hover state
        new_color = self.get_agent_color()
        self.agent_tile.border = border.all(4, new_color)
        self.label.color = new_color  # Update text color
        self.agent_tile.update()

    def remove_self(self, e):
        if self.agent_tile in self.parent_container.controls:
            print("list of added agents in class:",self.agent_list)
            self.agent_list.remove(self.agent_name)
            print("list of added agents in class:",self.agent_list)
            self.parent_container.controls.remove(self.agent_tile)
            self.parent_container.update()  # Update the UI to reflect changes

    def build_agent_card(self) -> Container:
        return self.agent_tile
    
class PlatformConfig:
    def __init__(self, name_field, all_adresses_checkbox, ports_field, submit_button, page):
        super().__init__()
        self.page = page

        #establish properties for agents
        self.agent_dropdown = self.numerate_agent_dropdown
        self.agent_column = Column()

        # initializes name field and pair for better formatting 
        self.name_field = name_field
        # making sure the on change functionality will check the validity of the text field
        self.name_field.on_change = self.validate_text
        self.name_field_pair = self.field_pair("Name", self.name_field)

        # initialize addresses field and pair for better formatting 
        self.all_adresses_checkbox = all_adresses_checkbox
        self.address_field_pair = self.field_pair("Adresses", self.all_adresses_checkbox)
        
        #initialize ports field and pair for better formatting 
        self.ports_field = ports_field
        self.ports_field_pair = self.field_pair("Ports", self.ports_field)
        
        #staic bus field because i kind of have no idea what that means
        self.bus_field_pair = self.field_pair("Bus Type", Text("2mg", size= 18, color="white"))

        #submit button passed in from program_card.py
        self.submit_button = submit_button
        
    def validate_text(self, e) -> None:
        valid_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
        input_text = e.control.value
        # Check if every character in the text is among the valid characters
        if all(c in valid_chars for c in input_text) and 0 <= len(input_text) <= 9:
            e.control.error_text = None  # Clear any previous error message
            self.submit_button.disabled = False
        else:
            error_messages = []
            if not all(c in valid_chars for c in input_text):
                error_messages.append("Only letters, numbers, and underscores are allowed.")
            e.control.error_text = " ".join(error_messages)
            self.submit_button.disabled = True
        self.submit_button.update()
        e.control.update()
    
    # Container containing the form title and form input pair
    def field_pair(self, text, input) -> Container:
        return  Container(
            height=70,
            padding=padding.only(top=10,bottom=10, left=5,right=5),
            content=Row(
                controls=[
                    Container(
                        expand=2,
                        content=Text(f"{text}",size=20)
                    ),
                    Container(
                        expand=3,
                        content=input
                    )
                ],
                spacing=0
            )
        )
    
    def divide_fields(self, field_list) -> list:
        div = Divider(height=9, thickness=3, color="white")
        #puts a divider in between each field pair in the field list 
        return [element for pair in zip(field_list, [div] * (len(field_list) - 1)) for element in pair] + [field_list[-1], div]
    
    def numerate_agent_dropdown(self)-> Dropdown:
        from volttron_installer.modules.all_agents import agents
        dropdown_options = []
        agent_list = agents
        for agent in agent_list:
            dropdown_options.append(dropdown.Option(text=agent))
        return Dropdown(
            options=[
                *dropdown_options
            ]
        )
    
    def add_agent(self, e) -> None:
        if self.agent_dropdown.value != None:
            if self.agent_dropdown.value not in added_agents:
                agent_tile_to_add = Agent(self.agent_dropdown, self.agent_column, added_agents).build_agent_card()
                self.agent_column.controls.append(agent_tile_to_add)
                self.page.update()
                added_agents.append(self.agent_dropdown)
                print(added_agents)
        print(self.agent_dropdown)

#Global scope
added_agents = []