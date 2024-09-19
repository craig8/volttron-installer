from flet import *
import flet as ft
import json
import yaml
from volttron_installer.components.platform_components.platform import Platform
from volttron_installer.modules.remove_from_controls import remove_from_selection
from volttron_installer.modules.styles import modal_styles2
from volttron_installer.modules.validate_field import check_json_field, check_yaml_field

class Agent:
    """
    A class that manages platform wide agent tiles, views, and handles the custom configuration
    of the agent.
    """
    counter = 0

    def __init__(self, shared_instance, agent_name, platform_agent_container, agent_config_container, agent_list):
        self.platform: Platform = shared_instance
        self.agent_name = agent_name
        self.platform_agent_container: Control = platform_agent_container
        self.agent_config_container: Control = agent_config_container

        # Same exact dict as shared instance of Platform
        self.added_agents = agent_list 
        self.custom_config = "" # Will be inputed into Platform's added_agents dict

        self.label = Text(value=self.agent_name, color=self.get_agent_color())
        self.input_json_field = TextField(multiline=True, label="Input Custom JSON or YAML")
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
            on_click=self.remove_agent_receiver,
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
                        content=Column(
                            [
                                self.input_json_field,
                                OutlinedButton(text="Save", on_click=self.check_yaml_submit)
                            ]
                        )
                    ),
                    self.error_message  # Display error message if JSON is invalid
                ]
            )
        )
        self.error_modal = AlertDialog(
            modal = False,
            content=Container(
                **modal_styles2(),
                height=150,
                content=Column(
                    [
                        Text("ERROR", size=22, color="red",),
                        Text(f"{self.error_message}"),
                        Text("Your custom configuration has not saved")
                    ]
                )
            )
        )
        self.agent_row = self.build_agent_row()


    def check_config_submit(self, e):
        custom_config: str = self.input_json_field.value
        if check_json_field(self.input_json_field):
            self.custom_config = custom_config
            pass
        elif check_json_field(self.input_json_field):
            self.custom_config = custom_config
            pass
        else:
            self.platform.page.open(self.error_modal)
            return


    def check_yaml_submit(self, e) -> None:
        yaml_string: str = self.input_json_field.value
        check_yaml_field(yaml_string)


    def get_agent_color(self):
        return "green"

    def check_json_submit(self, e) -> None:
        # Attempt to parse JSON input
        custom_json = self.input_json_field.value
        try:
            json.loads(custom_json)  # json.loads to validate JSON string
            self.custom_config = custom_json

            # Change the Agent's custom JSON in Platform instance
            self.added_agents[self.agent_name][1] = self.custom_config
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
    def remove_agent_receiver(self, e):
        self.platform.event_bus.publish("remove_agent")
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
                        on_click=self.remove_agent_receiver
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
