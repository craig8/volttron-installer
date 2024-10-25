from copy import deepcopy
from dataclasses import dataclass, field
from flet import *
import flet as ft
import json
import yaml
from volttron_installer.views.agent_setup import Agent
from volttron_installer.components import error_modal
from volttron_installer.components.platform_components.platform import Platform
from volttron_installer.modules.remove_from_controls import remove_from_selection
from volttron_installer.modules.styles import modal_styles2
from volttron_installer.modules.validate_field import check_json_field, check_yaml_field

@dataclass
class LocalAgent(Agent):
    platform: Platform
    
    def __post_init__(self) -> None:
        super().__post_init__()
        self.tile.content.controls[1].on_click = lambda e: self.platform.event_bus.publish("agent_removed", self)

    def clone_tile(self) -> None:
        tile = deepcopy(self.tile)
        return tile
    # Same exact dict as shared instance of Platform
    # NOTE any instance where agent_list is needed, is used by self.platform.added_agents
    # # aka, useless variable
    # def agent_config_functionality(self) -> Container:
    #     def check_config_submit(self, e):
    #         custom_config: str = self.input_json_field.value
    #         if check_yaml_field(self.input_json_field):
    #             self.custom_config = custom_config
    #             pass
    #         elif check_json_field(self.input_json_field):
    #             self.custom_config = custom_config
    #             pass
    #         else:
    #             self.platform.page.open(error_modal.error_modal())
    #             self.error_message.value = "Improper JSON or YAML was submitted, please try again"
    #             return

    #     def check_yaml_submit(self, e) -> None:
    #         yaml_string: str = self.input_json_field.value
    #         check_yaml_field(yaml_string)

    #     label = Text(value=self.agent_name)
    #     input_json_field = TextField(multiline=True, label="Input Custom JSON or YAML")
    #     error_message: Text = Text(value="", color="red")

    #     self.agent_row = self.build_agent_tile()
        
    #     # Individualized agent config menu
    #     agent_configuration_menu = Container(
    #         padding=5,
    #         content=Column(
    #             spacing=60,
    #             alignment=MainAxisAlignment.START,
    #             controls=[
    #                 Row(
    #                     wrap=True,
    #                     controls=[
    #                         Text(self.agent_name, size=24),
    #                     ]
    #                 ),
    #                 Container(
    #                     content=Column(
    #                         [
    #                             input_json_field,
    #                             OutlinedButton(text="Save", on_click=self.check_config_submit)
    #                         ]
    #                     )
    #                 ),
    #                 error_message  # Display error message if JSON is invalid
    #             ]
    #         )
    #     )
    #     return agent_configuration_menu

    # agent_configuration_menu: Container = field(init=False)

    # def __post_init__(self):
    #     self.agent_configuration_menu = self.agent_config_functionality()

    # def build_agent_configuration(self) -> Container:
    #     return self.agent_configuration_menu
