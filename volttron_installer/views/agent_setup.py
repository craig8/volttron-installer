from volttron_installer.components.base_tile import BaseForm, BaseTab, BaseTile
from flet import *
from volttron_installer.modules.attempt_to_update_control import attempt_to_update_control
from volttron_installer.modules.clean_json_string import clean_json_string
from volttron_installer.modules.global_configs import global_agents, global_drivers
from volttron_installer.modules.global_event_bus import global_event_bus
from volttron_installer.modules.remove_from_controls import remove_from_selection
from volttron_installer.modules.styles import modal_styles2
from dataclasses import dataclass, field
from volttron_installer.modules.populate_dropdowns import numerate_configs_dropdown
from volttron_installer.modules.validate_field import check_yaml_field, check_json_field
from volttron_installer.components.error_modal import error_modal

key_constructor =[
    "agent_name",
    "default_identity",
    "agent_path",
    "agent_configuration"
]

@dataclass
class Agent(BaseTile):
    agent_name: str
    default_identity: str
    agent_path: str
    agent_configuration: str

    tile: Container = field(init=False)
    
    def __post_init__(self):
        super().__init__(self.agent_name)  # Initialize BaseTile with agent_name
        self.tile = self.build_agent_tile()

    def build_agent_tile(self) -> Container:
        return self.build_tile()  # Calls BaseTile's build_tile method


class AgentForm(BaseForm):
    def __init__(self, agent, page: Page):
        self.agent_name_field = TextField(on_change=self.validate_fields)
        self.default_identity_field = TextField(on_change=self.validate_fields)
        self.agent_path_field = TextField(on_change=self.validate_fields)
        self.agent_configuration_field = TextField(hint_text="Input custom YAML or JSON", on_change=self.validate_fields, multiline=True)
        
        global_event_bus.subscribe("update_global_ui", self.update_ui)

        self.config_dropdown = numerate_configs_dropdown()
        self.modal_content = Column(
                        horizontal_alignment=CrossAxisAlignment.CENTER,
                        controls=[
                            Text("Edit Store Entries", size=20),
                            Row(
                                spacing = 10,
                                controls=[
                                    self.config_dropdown,
                                    Container()
                                ]
                            ),
                            Container(
                                margin=margin.only(bottom=-20),
                                padding=padding.only(left=25, right=25),
                                alignment=alignment.bottom_center,
                                content=Row(
                                    controls=[
                                        OutlinedButton(on_click=lambda e: self.page.close(self.modal),
                                                    content=Text("Cancel", color="red")),
                                        OutlinedButton(on_click=self.save_config_store_entries, 
                                                       text="Add")
                                    ],
                                    alignment=MainAxisAlignment.SPACE_BETWEEN
                                )
                            )
                        ]
                    )
        
        self.modal = AlertDialog(
                        modal = False,
                        bgcolor="#00000000",
                        content=Container(
                            **modal_styles2(),
                            width=400,
                            height=250,
                            content=self.modal_content
                        )
                    )

        self.added_config_entries_container = Container(
            margin=4,
            border_radius= 7,
            padding=5, 
            key="pass",
            expand=True,
            bgcolor=colors.with_opacity(0.45, "black"),
            content=Column(
                [
                    Text("Total Entries:")
                ],
                scroll=ScrollMode.AUTO
            )
        )

        form_fields = {
            "Name" : self.agent_name_field,
            "Default Identity" : self.default_identity_field,
            "Agent Path" : self.agent_path_field,
            "Agent Configuration" : self.agent_configuration_field,
            "Config Store Entries" : OutlinedButton(text="Add", on_click=lambda e: self.page.open(self.modal)),
            "store entries container" : self.added_config_entries_container
        }

        super().__init__(page, form_fields)
        self.agent: Agent = agent
        self.custom_config = self.agent.agent_configuration
        self.agent_config_validity = True
        self.agent_config_type: str | "YAML" | "JSON" = ""
        self.added_config_store_entries = {}
 
    def save_config_store_entries(self, e) -> None:
        if self.config_dropdown.value not in self.added_config_store_entries:
            self.added_config_store_entries[self.config_dropdown.value] = global_drivers[self.config_dropdown.value]
            self.added_config_entries_container.content.controls.append(self.create_added_entry_tile(self.config_dropdown.value))
        attempt_to_update_control(self.added_config_entries_container)
        self.page.close(self.modal)

    def update_ui(self, var = None)-> None:
        self.config_dropdown = numerate_configs_dropdown()
        attempt_to_update_control(self.config_dropdown)

    def create_added_entry_tile(self, title: str) -> Container:
        tile_instance = BaseTile(title=title)
        tile = tile_instance.build_tile()
        tile.content.controls[1].on_click = lambda e: self.remove_from_added_entries(title, id=tile.key)
        return tile

    def remove_from_added_entries(self, title: str, id: str) -> None:
        del self.added_config_store_entries[title]
        remove_from_selection(self.added_config_entries_container.content, id)

    def validate_fields(self, e) -> None:
        # Implement field validation logic and toggle submit button state.
        fields = [self.form_fields[i] for i in self.form_fields.keys() if isinstance(self.form_fields[i], TextField)]
        valid = all(field.value for field in fields)

        if self.agent_config_validity == False:
            self.toggle_submit_button(False)
        else:
            self.toggle_submit_button(valid)

    def check_agent_config_field(self) -> bool:
        custom_config: str = self.agent_configuration_field.value
        if check_yaml_field(self.agent_configuration_field):
            self.custom_config = custom_config
            self.agent_config_type = "YAML"
            return True
        elif check_json_field(self.agent_configuration_field):
            self.custom_config = custom_config
            self.agent_config_type = "JSON"
            return True
        else:
            self.page.open(error_modal())
            return False
        
    async def save_config(self, e) -> None:
        valid_config = self.check_agent_config_field()
        if valid_config == False:
            return

        old_name = self.agent.agent_name

        check_overwrite: bool | None = await self.detect_conflict(global_agents, self.agent_name_field.value, self.agent.agent_name)

        if check_overwrite == True:
            global_event_bus.publish("soft_remove", self.agent.tile.key)

        elif check_overwrite == False:
            return

        # Save field values to agent attributes
        self.agent.default_identity = self.default_identity_field.value
        self.agent.agent_path = self.agent_path_field.value
        self.agent.agent_configuration = clean_json_string(self.agent_configuration_field.value)
        self.agent.agent_name = self.agent_name_field.value

        dictionary_appendable = {
            "default_identity" : self.agent.default_identity,
            "agent_path" : self.agent.agent_path,
            "agent_configuration" : self.agent.agent_configuration if self.agent_config_type == "YAML" else eval(self.agent.agent_configuration),
            "config_store_entries" : self.added_config_store_entries
        }

        if check_overwrite == "rename":
            self.replace_key(global_agents, old_key=old_name, new_key=self.agent.agent_name)
        global_agents[self.agent.agent_name] = dictionary_appendable

        self.agent.tile.content.controls[0].value = self.agent.agent_name
        attempt_to_update_control(self.page)
        self.write_to_file("agents", global_agents)
        update_global_ui()

class AgentSetupTab(BaseTab):
    def __init__(self, page: Page) -> None:
        self.list_of_agents = Column(
            expand=2,
            controls=[
                OutlinedButton(text="Setup an Agent", on_click=self.add_new_agent)
            ]
        )
        super().__init__(self.list_of_agents, page)
        self.page = page
        self.agent_tab_view = self.tab

        global_event_bus.subscribe("tab_change", self.tab_change)

    def tab_change(self, selected_tab):
        self.refresh_tiles("agents", global_agents, Agent, AgentForm)

    def add_new_agent(self, e) -> None:
        self.add_new_tile(global_agents, "agents", Agent, AgentForm)

    def build_agent_setup_tab(self) -> Container:
        return self.agent_tab_view

def update_global_ui():
    global_event_bus.publish("update_global_ui", None)