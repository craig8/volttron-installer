from flet import *
import flet as ft
import json
from volttron_installer.modules.remove_from_controls import remove_from_selection

class Agent:
    counter = 0

    def __init__(self, agent_name, platform_agent_container, agent_config_container, agent_list):
        self.agent_name = agent_name
        self.platform_agent_container: Control = platform_agent_container
        self.agent_config_container: Control = agent_config_container

        # Same exact dict as shared instance of Platform
        self.added_agents = agent_list 
        self.custom_json = "" # Will be inputed into Platform's added_agents dict

        self.label = Text(value=self.agent_name, color=self.get_agent_color())
        self.input_json_field = TextField(label="Input Custom JSON", on_submit=self.check_json_submit)
        self.error_message = Text(value="", color="red")
        
        # View agent instances to give correct keys to specific components
        self.agent_id = Agent.counter
        Agent.counter += 1

        # Initialize container with default agent color
        self.agent_tile = Container(
            key=f"agent_tile_{self.agent_id}",
            border_radius=10,
            padding=5,
            border=border.all(4, self.get_agent_color()),
            on_click=self.remove_self,
            content=self.label,
        )

        # Individualized agent config menu
        self.agent_configuration_menu = Container(
            padding=5,
            content=Column(
                spacing=60,
                alignment=MainAxisAlignment.START,
                controls=[
                    Row(
                        wrap=True,
                        controls=[
                            Text(self.agent_name, size=24),
                        ]
                    ),
                    Container(
                        content=self.input_json_field
                    ),
                    self.error_message  # Display error message if JSON is invalid
                ]
            )
        )
        self.agent_row = self.build_agent_row()


    def get_agent_color(self):
        return "green"

    def check_json_submit(self, e) -> None:
        # Attempt to parse JSON input
        custom_json = self.input_json_field.value
        try:
            json.loads(custom_json)  # json.loads to validate JSON string
            self.custom_json = custom_json

            # Change the Agent's custom JSON in Platform instance
            self.added_agents[self.agent_name][1] = self.custom_json
            self.error_message.value = ""  # Clear error message if JSON is valid
        except json.JSONDecodeError:
            self.error_message.value = "You've submitted improper JSON"
        
        # Update UI elements to reflect changes
        self.error_message.update()
        self.input_json_field.update()


    def remove_agent_from_selection(self) -> None:
        # Find the index of the container with the unique identifier (key)
        def find_container_index() -> int:
            for index, control in enumerate(self.agent_config_container.controls):
                if isinstance(control, Container) and control.key == self.agent_row.key:
                    return index
            return -1  # Return -1 if the container key is not found

        # Attempt to remove the found container and update the UI
        try:
            container_index = find_container_index()
            if container_index != -1:
                del self.agent_config_container.controls[container_index]
                self.agent_config_container.update()
            else:
                print("The agent row is not found in the container controls list.")
        except ValueError as e:
            print(f"An error occurred: {e}")
            print("The agent row is not found in the container controls list.")


    # delete self from added agents in platform instance, and all containers that contain itself
    def remove_self(self, e):
        if self.agent_tile in self.platform_agent_container.controls:
            del self.added_agents[self.agent_name]
            self.platform_agent_container.controls.remove(self.agent_tile)
            self.platform_agent_container.update()
            # Also delete from agent container in agent config
            remove_from_selection(self.agent_config_container, self.agent_row.key)

    def build_agent_row(self):
        agent_card = self.build_agent_card()
        agent_row_stack = Stack(
            key=f"agent_row_stack_{self.agent_id}",
            controls=[
                Container(alignment=alignment.center_left, content=agent_card),
                Container(
                    alignment=alignment.center_right,
                    content=IconButton(
                        icon=icons.DELETE,
                        on_click=self.remove_self # Ensure correct invocation of the method
                    )
                )
            ]
        )

        agent_row = Container(
            key=f"agent_row_{self.agent_id}",
            height=70,
            content=agent_row_stack 
        )
        return agent_row

    def build_agent_card(self) -> Container:
        return self.agent_tile

    def build_agent_configuration(self) -> Container:
        return self.agent_configuration_menu
