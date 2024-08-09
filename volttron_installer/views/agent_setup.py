from dataclasses import dataclass
from flet import *
import json
from volttron_installer.modules.field_methods import field_pair, divide_fields
from volttron_installer.modules.global_configs import global_agents
from volttron_installer.components.default_tile_styles import build_default_tile

# this whole file is basically a copy of hosts_tab.py hahahaahahpfioahah aaawawpb
# ok so when i properly save an agent, its going to publish an event_bus called
# update all agent dropdowns,
# when i save a good agent its going to write to a file where platform will take it
# in, platform is also going to subscribe to update agents because it is going to take in
# new agents that have been configured so in essence,
#
# call event bus on submit -> platform subscribes and so does every dropwdown, everyone updates
@dataclass
class Agent:
    """Host object, will store nessary info and write to a file"""
    agent_name: str
    default_identity: str
    agent_path: str
    agent_configuration: str
    ssh_port: str # string for now

    def remove_self(self, e) -> None:
        print("Yeah, agent_setup.py self.remove works")

    def build_agent_tile(self) -> Container:
        agent_tile = build_default_tile(self.agent_name)
        agent_tile.content.controls[1].on_click = self.remove_self
        return agent_tile

class FormTemplate:
    def __init__(self, page: Page, agent: Agent, host_tile: Container):
        self.page = page
        self.agent = agent
        self.agent_tile = host_tile

        self.agent_name_field = TextField(on_change=self.validate_submit)
        self.default_identity_field = TextField(on_change=self.validate_submit)
        self.agent_path_field = TextField(on_change=self.validate_submit)
        self.agent_configuration_field = TextField(value="",on_change=self.validate_submit)
        self.config_store_entry_key = RadioGroup(
                                        value="",
                                        on_change=self.validate_submit,
                                        content=Row(
                                            controls=[
                                                Radio(value="csv", label="CSV"),
                                                Radio(value="json", label="JSON"),
                                            ]
                                        )
                                    )
        self.formatted_fields: list = divide_fields([
                        field_pair("Name", self.agent_name_field),
                        field_pair("Default Identity", self.default_identity_field),
                        field_pair("Agent Path", self.agent_path_field),
                        field_pair("Agent Configuration", self.agent_configuration_field),
                        field_pair("Config Store Entry Key", self.config_store_entry_key)
                        ])
        self.submit_button = OutlinedButton(text="Save", disabled=True, on_click=self.save_host_config)
        self._form = Column(
                        expand=3,
                        controls=[
                            *self.formatted_fields,
                            self.submit_button,
                        ]
                    )
        
    def save_host_config(self, e):
        self.agent.default_identity = self.default_identity_field.value
        self.agent.agent_path = self.agent_path_field.value
        self.agent.agent_configuration = self.agent_configuration_field.value
        self.agent.ssh_port = self.config_store_entry_key.value
        # Save old name to variable
        old_name = self.agent.agent_name
        # Then re-assign new name
        self.agent.agent_name = self.agent_name_field.value

        if old_name in global_agents.keys():
            # Re-assign new name to agent
            global_agents[self.agent.agent_name] = global_agents.pop(old_name)
            agent_dict = global_agents[self.agent.agent_name]

            # Update agent details
            agent_dict["default_identity"] = self.agent.default_identity
            agent_dict["agent_path"] = self.agent.agent_path
            agent_dict["agent_configuration"] = self.agent.agent_configuration

        else:
            agent_dictionary_appendable = {
                "default_identity": self.agent.default_identity,
                "agent_path": self.agent.agent_path,
                "agent_configuration": self.agent.agent_configuration,
            }
            global_agents[self.agent.agent_name] = agent_dictionary_appendable

        self.agent_tile.content.controls[0].value = self.agent.agent_name
        self.page.update()
        print(global_agents)

    def check_json_submit(self, field: TextField) -> None:
        # Attempt to parse JSON input
        custom_json = field.value
        if custom_json == "" :
            field.border_color = "black"
            field.update()
            return True
        
        try:
            json.loads(custom_json)  # json.loads to validate JSON string
            self.custom_json = custom_json

            # Update valid field ui
            field.border_color = colors.GREEN
            field.color = "white"
            field.update()
            return True
        except json.JSONDecodeError:
            field.border_color=colors.RED_800
            field.color = colors.RED_800
            field.update()
            return False

    def validate_submit(self, e)-> None:
        if (
            self.agent_name_field.value and
            self.agent_configuration_field.value and
            self.agent_path_field.value and
            self.config_store_entry_key.value and
            self.default_identity_field.value != "" and
            self.check_json_submit(self.agent_configuration_field) == True
        ):
            self.submit_button.disabled = False
        else:
            self.submit_button.disabled = True
        self.submit_button.update()
    
    def build_agent_form(self) -> Column:
        return self._form


class AgentSetupTab:
    def __init__(self, page: Page) -> None:
        self.page = page

        self.placeholder=Column(
            expand=3
        )
        self.list_of_hosts = Column(
                                expand=2,
                                controls=[
                                    OutlinedButton(text="Setup an Agent", on_click=self.add_new_agent)
                                ]
                            )
        self.agent_tab_view=Container(
                                padding=padding.only(left=10),
                                margin=margin.only(left=10, right=10, bottom=5, top=5),
                                bgcolor="#20f4f4f4",
                                border_radius=12,
                                content=Row(
                                    controls=[
                                        self.list_of_hosts,
                                        VerticalDivider(color="white", width=9, thickness=3),
                                        self.placeholder
                                    ]
                                )
                            ) 

    def add_new_agent(self, e) -> None:
        new_host = Agent(
                agent_name="New Agent",
                default_identity="",
                agent_path="",
                agent_configuration="",
                ssh_port=""
            )
        host_tile = new_host.build_agent_tile()
        host_form = FormTemplate(self.page, new_host, host_tile)
        host_tile.on_click=lambda e: self.agent_is_selected(e, host_form, host_tile)
        self.list_of_hosts.controls.append(host_tile)
        self.list_of_hosts.update()


    def agent_is_selected(self, e, host_form: FormTemplate, host_tile: Container) -> None:
        self.agent_tab_view.content.controls[2] = host_form.build_agent_form()
        self.page.update()


    def build_agent_setup_tab(self)-> Container:
        return self.agent_tab_view