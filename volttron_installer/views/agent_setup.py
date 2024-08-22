from volttron_installer.components.base_tile import BaseForm, BaseTab, BaseTile
from flet import *
from volttron_installer.modules.global_configs import global_agents, find_dict_index
from volttron_installer.modules.global_event_bus import global_event_bus
from dataclasses import dataclass, field
import json

from volttron_installer.platform_tabs.agent_config import AgentConfig

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

    agent_tile: Container = field(init=False)
    
    def __post_init__(self):
        super().__init__(self.agent_name)  # Initialize BaseTile with agent_name
        self.agent_tile = self.build_agent_tile()

    def build_agent_tile(self) -> Container:
        return self.build_tile()  # Calls BaseTile's build_tile method


class AgentForm(BaseForm):
    def __init__(self, agent, page: Page):
        self.agent_name_field = TextField(on_change=self.validate_fields)
        self.default_identity_field = TextField(on_change=self.validate_fields)
        self.agent_path_field = TextField(on_change=self.validate_fields)
        self.agent_configuration_field = TextField(on_change=lambda e: self.check_json_submit(e, self.agent_configuration_field))
        form_fields = {
            "Name" : self.agent_name_field,
            "Default Identity" : self.default_identity_field,
            "Agent Path" : self.agent_path_field,
            "Agent Configuration" : self.agent_configuration_field,
        }

        super().__init__(page, form_fields)
        self.agent: Agent = agent
        self.json_validity = True
 
    def validate_fields(self, e) -> None:
        # Implement field validation logic and toggle submit button state.
        fields = [self.form_fields[i] for i in self.form_fields.keys()]
        valid = all(field.value for field in fields)
        if self.json_validity == False:
            self.toggle_submit_button(False)
        else:
            self.toggle_submit_button(valid)

    def save_config(self, e) -> None:
        # Save field values to agent attributes
        self.agent.default_identity = self.default_identity_field.value
        self.agent.agent_path = self.agent_path_field.value
        self.agent.agent_configuration = self.agent_configuration_field.value

        # Save old name to a variable so we can see if it was originally in global_agents
        old_name = self.agent.agent_name
        index = find_dict_index(global_agents, old_name)

        # Now we can reassign new name
        self.agent.agent_name = self.agent_name_field.value

        if index is not None:
            for key, val in zip(key_constructor, self.val_constructor):
                global_agents[index][key] = val.value
        else:
            agent_dictionary_appendable = {}
            for key, val in zip(key_constructor, self.val_constructor):
                agent_dictionary_appendable[key] = val.value
            global_agents.append(agent_dictionary_appendable)

        self.agent.agent_tile.content.controls[0].value = self.agent.agent_name
        self.page.update()
        self.write_to_file("agents", global_agents)
        update_global_ui()



    def check_json_submit(self, e, field: TextField) -> None:
        """
        Validates the JSON input in a text field.

        Args:
            field (TextField): The text field containing JSON input.
        """
        custom_json = field.value
        if custom_json == "" or None or " ":
            field.border_color = "black"
            field.update()
            self.json_validity = True
        try:
            json.loads(custom_json)
            field.border_color = colors.GREEN
            field.color = "white"
            field.update()
            self.json_validity = True
        except json.JSONDecodeError:
            field.border_color = colors.RED_800
            field.color = colors.RED_800
            field.update()
            self.json_validity = False
        self.validate_fields(e= e)
        
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
        if selected_tab == 1:
            for agent in global_agents:
                refreshed_agent = Agent(
                                    agent_name = agent["agent_name"],
                                    default_identity= agent["default_identity"],
                                    agent_path= agent["agent_path"],
                                    agent_configuration= agent["agent_configuration"]
                                )
                refreshed_form = AgentForm(refreshed_agent, self.page)
                self.refresh_tiles(global_agents, refreshed_agent, refreshed_agent.agent_tile, refreshed_form, "agents")

    def add_new_agent(self, e) -> None:
        self.add_new_tile(global_agents, "agents", Agent, AgentForm)

    def build_agent_setup_tab(self) -> Container:
        return self.agent_tab_view

def update_global_ui():
    global_event_bus.publish("update_global_ui", None)