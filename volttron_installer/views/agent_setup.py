from dataclasses import dataclass
from flet import *
import json
from volttron_installer.modules.write_to_json import write_to_agents
from volttron_installer.modules.field_methods import field_pair, divide_fields
from volttron_installer.modules.global_configs import global_agents, find_dict_index
from volttron_installer.components.default_tile_styles import build_default_tile
from volttron_installer.modules.styles import modal_styles

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

    def remove_self(self, e) -> None:
        print("Yeah, agent_setup.py self.remove works")
        index = find_dict_index(global_agents, self.agent_name)
        if index is not None:
            global_agents.pop(index)
            writting_to_agents()
        else:
            print("agent isnt even properly made")
        #method to remove from parent container

    def build_agent_tile(self) -> Container:
        agent_tile = build_default_tile(self.agent_name)
        agent_tile.content.controls[1].on_click = self.remove_self
        return agent_tile

class FormTemplate:
    def __init__(self, page: Page, agent: Agent, host_tile: Container):
        self.page = page
        self.agent = agent
        self.agent_tile = host_tile

        # ======================================== Registering modal and stuff==========================
        self.name_field = TextField(color="black", label="Name", on_change=self.validate_config_entry)
        self.csv_radio = Radio(value="csv")
        self.json_radio = Radio(value="json")
        self.add_config_button = OutlinedButton(
                                    content=Text("Add", color="black"),
                                    disabled=True
                                )
        self.type_radio_group = RadioGroup(
            value="",
            on_change=self.validate_config_entry,
            content=Row(
                spacing=25,
                controls=[
                    self.radio_title_grouper(self.csv_radio),
                    self.radio_title_grouper(self.json_radio)
                ],
                alignment=MainAxisAlignment.CENTER,
            )
        )
        self.modal_content = Column(
            spacing=30,
            horizontal_alignment=CrossAxisAlignment.CENTER,
            controls=[
                Text("Add a Configuration", size=20, color="black"),
                Container(
                    alignment=alignment.center,
                    content=self.type_radio_group
                ),
                Container(
                    padding=padding.only(left=20, right=20),
                    content=self.name_field
                ),
                Container(
                    margin=margin.only(bottom=-20),
                    padding=padding.only(left=25, right=25),
                    alignment=alignment.bottom_center,
                    content=Row(
                        controls=[
                            OutlinedButton(on_click=lambda e: self.page.close(self.add_config_modal),
                                           content=Text("Cancel", color="red")),
                            self.add_config_button
                        ],
                        alignment=MainAxisAlignment.SPACE_BETWEEN
                    )
                )
            ]
        )
        self.add_config_modal = AlertDialog(
            modal=False,
            bgcolor="#00000000",
            content=Container(
                **modal_styles(),
                width=400,
                height=250,
                content=self.modal_content
            ),
        )

#=============================================== END OF MODAL STUFF======================================

        # The actual form stuff 
        self.agent_name_field = TextField(on_change=self.validate_submit)
        self.default_identity_field = TextField(on_change=self.validate_submit)
        self.agent_path_field = TextField(on_change=self.validate_submit)
        self.agent_configuration_field = TextField(value="",on_change=self.validate_submit)
        self.config_store_entry_key = OutlinedButton(text="Click Me!", on_click=lambda e: self.page.open(self.add_config_modal))
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

    def validate_config_entry(self, e) -> None:
        if self.name_field.value and self.type_radio_group.value !="":
            self.add_config_button.disabled = False
        else:
            self.add_config_button.disabled = True
        self.add_config_button.update()

    def radio_title_grouper(self, radio: Radio) -> Row:
        label = radio.value.upper()
        return Row(
            alignment=MainAxisAlignment.CENTER,
            spacing=-10,
            controls=[
                radio,
                Text(label, color="black")
            ]
        )

        
    def save_host_config(self, e):
        self.agent.default_identity = self.default_identity_field.value
        self.agent.agent_path = self.agent_path_field.value
        self.agent.agent_configuration = self.agent_configuration_field.value
        #self.agent.ssh_port = self.config_store_entry_key.value
        
        
        # Save old name to variable
        old_name = self.agent.agent_name

        index = find_dict_index(global_agents, old_name)

        # Then re-assign new name
        self.agent.agent_name = self.agent_name_field.value

        if index is not None:
            # Re-assign new name to agent and update details
            global_agents[index]["agent_name"] = self.agent.agent_name
            global_agents[index]["default_identity"] = self.agent.default_identity
            global_agents[index]["agent_path"] = self.agent.agent_path
            global_agents[index]["agent_configuration"] = self.agent.agent_configuration

        else:
            agent_dictionary_appendable = {
                "agent_name" : self.agent.agent_name,
                "default_identity": self.agent.default_identity,
                "agent_path": self.agent.agent_path,
                "agent_configuration": self.agent.agent_configuration,
            }
            global_agents.append(agent_dictionary_appendable)

        self.agent_tile.content.controls[0].value = self.agent.agent_name
        self.page.update()

        from volttron_installer.modules.write_to_json import write_to_agents # writing to a file 
        write_to_agents(global_agents)

    def check_json_submit(self, field: TextField) -> None:
        # Attempt to parse JSON input
        custom_json = field.value
        if custom_json == "" : # if custom json config is blank because you could just choose not to have config
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
            #self.config_store_entry_key.value and
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
                agent_configuration=""
                #ssh_port=""
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
    
# Im lazy...
def writting_to_agents() -> None : write_to_agents(global_agents)