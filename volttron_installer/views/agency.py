from dataclasses import dataclass, field
from flet import *
import json
from volttron_installer.modules.write_to_json import write_to_agents
from volttron_installer.modules.create_field_methods import field_pair, divide_fields
from volttron_installer.modules.global_configs import global_agents, find_dict_index
from volttron_installer.components.default_tile_styles import build_default_tile
from volttron_installer.modules.styles import modal_styles
from volttron_installer.modules.remove_from_controls import remove_from_selection

@dataclass
class Agent:
    """
    A class representing an individual Agent used for configuration.

    Attributes:
        agent_name (str): The name of the agent.
        default_identity (str): The default identity for the agent.
        agent_path (str): The path where the agent is located.
        agent_configuration (str): The configuration details of the agent.
        id_key (int): A unique identifier key for the agent.
    """
    counter = 0
    agent_name: str
    default_identity: str
    agent_path: str
    agent_configuration: str
    id_key: int = field(init=False)

    def __post_init__(self):
        """
        Post-initialization to set the id_key and increment the counter.
        """
        self.id_key = Agent.counter
        Agent.counter += 1

    def build_agent_tile(self) -> Container:
        agent_tile = build_default_tile(self.agent_name)
        agent_tile.key = self.id_key
        return agent_tile

class FormTemplate:
    """
    A class to handle the form template for agent registration and management.

    Attributes:
        agent_tab_view (Container): The main container view for the agent tab.
        list_of_agents (Column): A column containing the list of agents.
        page (Page): The Flet page where the components are rendered.
        agent (Agent): The agent being handled by the form.
        agent_tile (Container): The agent tile container on the UI.
    """
    def __init__(self, agent_tab_view, list_of_agents, page: Page, agent: Agent, agent_tile: Container):
        self.page = page
        self.agent = agent
        self.agent_tile = agent_tile
        self.agent_tab_view = agent_tab_view
        self.list_of_agents = list_of_agents
        self.agent_tile.content.controls[1].on_click = self.remove_self

        # Registering Components and Modal for Adding a Configuration
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

        # Form Fields for Agent Registration
        self.agent_name_field = TextField(on_change=self.validate_submit)
        self.default_identity_field = TextField(on_change=self.validate_submit)
        self.agent_path_field = TextField(on_change=self.validate_submit)
        self.agent_configuration_field = TextField(value="", on_change=self.validate_submit)
        self.config_store_entry_key = OutlinedButton(text="Click Me!", on_click=lambda e: self.page.open(self.add_config_modal))
        self.formatted_fields: list = divide_fields([
            field_pair("Name", self.agent_name_field),
            field_pair("Default Identity", self.default_identity_field),
            field_pair("Agent Path", self.agent_path_field),
            field_pair("Agent Configuration", self.agent_configuration_field),
            field_pair("Config Store Entry Key", self.config_store_entry_key)
        ])
        self.submit_button = OutlinedButton(text="Save", disabled=True, on_click=self.save_agent_config)
        self._form = Column(
            expand=3,
            controls=[
                *self.formatted_fields,
                self.submit_button,
            ]
        )

    def remove_self(self, e) -> None:
        """
        Removes the agent from the global agent list and updates the UI.
        """
        index = find_dict_index(global_agents, self.agent.agent_name)
        if index is not None:
            global_agents.pop(index)
            writting_to_agents()
        else:
            print("The agent you are trying to remove hasn't been properly registered yet.")
        remove_from_selection(self.list_of_agents, self.agent.id_key)
        self.agent_tab_view.content.controls[2] = Column(expand=3)
        self.page.update()

    def validate_config_entry(self, e) -> None:
        """
        Validates the configuration entry fields and enables/disables the submit button accordingly.
        """
        if self.name_field.value and self.type_radio_group.value != "":
            self.add_config_button.disabled = False
        else:
            self.add_config_button.disabled = True
        self.add_config_button.update()

    def radio_title_grouper(self, radio: Radio) -> Row:
        """
        Creates a row combining a radio button with its label.

        Args:
            radio (Radio): The radio button for which to create the label.

        Returns:
            Row: A row containing the radio button and its label, styling reasons.
        """
        label = radio.value.upper()
        return Row(
            alignment=MainAxisAlignment.CENTER,
            spacing=-10,
            controls=[
                radio,
                Text(label, color="black")
            ]
        )

    def save_agent_config(self, e):
        """
        Saves the host configuration and updates the global agent list.
        """
        self.agent.default_identity = self.default_identity_field.value
        self.agent.agent_path = self.agent_path_field.value
        self.agent.agent_configuration = self.agent_configuration_field.value

        old_name = self.agent.agent_name
        index = find_dict_index(global_agents, old_name)
        self.agent.agent_name = self.agent_name_field.value

        if index is not None:
            global_agents[index]["agent_name"] = self.agent.agent_name
            global_agents[index]["default_identity"] = self.agent.default_identity
            global_agents[index]["agent_path"] = self.agent.agent_path
            global_agents[index]["agent_configuration"] = self.agent.agent_configuration
        else:
            agent_dictionary_appendable = {
                "agent_name": self.agent.agent_name,
                "default_identity": self.agent.default_identity,
                "agent_path": self.agent.agent_path,
                "agent_configuration": self.agent.agent_configuration,
            }
            global_agents.append(agent_dictionary_appendable)

        self.agent_tile.content.controls[0].value = self.agent.agent_name
        self.page.update()
        write_to_agents(global_agents)

    def check_json_submit(self, field: TextField) -> None:
        """
        Validates the JSON input in a text field.

        Args:
            field (TextField): The text field containing JSON input.
        """
        custom_json = field.value
        if custom_json == "":
            field.border_color = "black"
            field.update()
            return True

        try:
            json.loads(custom_json)
            field.border_color = colors.GREEN
            field.color = "white"
            field.update()
            return True
        except json.JSONDecodeError:
            field.border_color = colors.RED_800
            field.color = colors.RED_800
            field.update()
            return False

    def validate_submit(self, e) -> None:
        """
        Validates the agent form fields and enables/disables the submit button accordingly.
        """
        if (
            self.agent_name_field.value and
            self.agent_configuration_field.value and
            self.agent_path_field.value and
            self.default_identity_field.value != "" and
            self.check_json_submit(self.agent_configuration_field)
        ):
            self.submit_button.disabled = False
        else:
            self.submit_button.disabled = True
        self.submit_button.update()

    def build_agent_form(self) -> Column:
        return self._form

class AgentSetupTab:
    """
    A class to manage the Agent Setup Tab interface.

    Attributes:
        page (Page): The Flet page where the components are rendered.
    """
    def __init__(self, page: Page) -> None:
        self.page = page
        self.placeholder = Column(expand=3)
        self.list_of_agents = Column(
            expand=2,
            controls=[
                OutlinedButton(text="Setup an Agent", on_click=self.add_new_agent)
            ]
        )
        self.agent_tab_view = Container(
            padding=padding.only(left=10),
            margin=margin.only(left=10, right=10, bottom=5, top=5),
            bgcolor="#20f4f4f4",
            border_radius=12,
            content=Row(
                controls=[
                    self.list_of_agents,
                    VerticalDivider(color="white", width=9, thickness=3),
                    self.placeholder
                ]
            )
        )

    def add_new_agent(self, e) -> None:
        """
        Adds a new agent and its corresponding form for setup.
        """
        new_agent = Agent(
            agent_name="New Agent",
            default_identity="",
            agent_path="",
            agent_configuration=""
        )
        agent_tile = new_agent.build_agent_tile()
        agent_form = FormTemplate(
            self.agent_tab_view,
            self.list_of_agents,
            self.page,
            new_agent,
            agent_tile
        )
        # Immediately assign the on_click function
        agent_tile.on_click = lambda e: self.agent_is_selected(e, agent_form)
        self.list_of_agents.controls.append(agent_tile)
        self.list_of_agents.update()

    def agent_is_selected(self, e, agent_form: FormTemplate) -> None:
        """
        Displays the form for the selected agent.

        Args:
            e: The event object.
            agent_form (FormTemplate): The form template for the selected agent.
        """
        self.agent_tab_view.content.controls[2] = agent_form.build_agent_form()
        self.page.update()

    def build_agent_setup_tab(self) -> Container:
        """
        Builds and returns the main container for the Agent Setup Tab.
        """
        return self.agent_tab_view

# Function to write the agent data to a file
def writting_to_agents() -> None:
    write_to_agents(global_agents)
