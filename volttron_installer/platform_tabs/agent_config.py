from re import A
from flet import *
from volttron_installer.components.agent import LocalAgent
from volttron_installer.components.platform_components.platform import Platform
from volttron_installer.modules.populate_dropdowns import numerate_agent_dropdown
from volttron_installer.modules.global_configs import agent_specific_configs, global_agents
from volttron_installer.platform_tabs import local_config_store
from volttron_installer.modules.attempt_to_update_control import attempt_to_update_control
from volttron_installer.modules.remove_from_controls import remove_from_selection
from volttron_installer.modules.show_selected_tile import show_selected_tile
import yaml

class AgentConfig:
    def __init__(self, shared_instance: Platform) -> None:

        # Initialize the shared isntance of Platform
        self.platform: Platform = shared_instance

        # Subscribe to event
        self.platform.event_bus.subscribe("update_global_ui", self.update_self_ui)
        self.platform.event_bus.subscribe("write_to_platform", self.write_agents_to_platform)
        self.platform.event_bus.subscribe("append_your_agent", self.append_agent)
        self.platform.event_bus.subscribe("remove_your_agent", self.remove_agent)

        self.agent_dropdown = numerate_agent_dropdown()
        self.add_agent_button =Container(key='DO NOT HURT ME',
                          width=40,
                          content=IconButton(icon=icons.ADD_CIRCLE_OUTLINE_ROUNDED,
                                             on_click=self.add_agent,
                                             icon_color="white"))
        # Platform agent column and Agent config column
        self.agent_config_column: Column = Column(
            expand=3,
            scroll=ScrollMode.AUTO,
            alignment=MainAxisAlignment.START,
            controls=[
                self.agent_dropdown,
                self.add_agent_button
            ]
        )

        # Immediately append necessary components
        # Control holding a placeholder until an agent has been selected, which will
        # replace this placeholder with the agent's own configuration view
        self.configure_agent_view = Container(
            expand=3, 
            content=Container(
                    # Place holder text
                    content=Text("Select an agent to configure!")
                )
            )

        self.divider = VerticalDivider(color="white", width=9, thickness=3)
        self._comprehensive_view = Column(
            controls=[
                Container(
                    height=600,
                    margin=margin.only(left=10, right=10, bottom=5, top=5),
                    bgcolor="#20f4f4f4",
                    border_radius=12,
                    content=Row(
                        controls=[
                            self.agent_config_column,
                            self.divider,
                            self.configure_agent_view
                        ]
                    )
                ),
                Container(
                    height=900
                )
            ],
            scroll=ScrollMode.AUTO
        )

    def agent_config_section(self, agent: LocalAgent) -> None:
        
        def write_to_platform(data=None):
            # print("this is our agent type shi", agent)
            # print("this is what we got in platform", self.platform.added_agents[agent.agent_name])
            self.platform.added_agents[agent.agent_name]["agent_configuration"] = agent.agent_configuration

        def check_config_submit(field: TextField):
            from volttron_installer.modules.validate_field import check_yaml_field, check_json_field
            from volttron_installer.components.error_modal import error_modal
            from volttron_installer.modules.clean_json_string import clean_json_string
            custom_config: str = field.value
            if check_json_field(field):
                # print("JSON")
                agent.agent_configuration = clean_json_string(custom_config)
            elif check_yaml_field(field):
                agent.agent_configuration = custom_config
            else:
                self.platform.page.open(error_modal())
                return
            # print("yooo i just saved an agent config", agent.agent_configuration)

        self.platform.event_bus.subscribe("publish_commits", write_to_platform)
            
        input_json_field = TextField(
                                multiline=True, 
                                value=agent.agent_configuration, 
                                label="Input Custom JSON or YAML"
                            )
        agent_configuration_menu = Container(
            padding=5,
            content=Column(
                spacing=60,
                alignment=MainAxisAlignment.START,
                controls=[
                    Row(
                        wrap=True,
                        controls=[
                            Text(agent.agent_name, size=24),
                        ]
                    ),
                    Container(
                        content=Column(
                            [
                                input_json_field,
                                OutlinedButton(text="Save", on_click=lambda e: check_config_submit(input_json_field))
                            ]
                        )
                    ),
                ]
            )
        )
        return agent_configuration_menu

    def write_agents_to_platform(self, data=None) -> None:
        #self.platform.added_agents = self.add_agent
        pass

    def update_self_ui(self, data= None):
        updated_agent_dropdown = numerate_agent_dropdown()
        self.agent_config_column.controls[0] = updated_agent_dropdown
        self.platform.page.update()

    def forward_agent_removed(self, agent: LocalAgent) -> None:
        self.platform.event_bus.publish("agent_removed", agent)

    def remove_agent(self, agent: LocalAgent) -> None:
        key: str = agent.tile.key
        remove_from_selection(self.agent_config_column, key)

    def forward_agent_appended(self, agent_name: str) -> None:
        self.platform.event_bus.publish("agent_appended", agent_name)

    def append_agent(self, agent: LocalAgent) -> None:
        agent_tile = agent.clone_tile()
        agent_tile.on_click = lambda e: self.display_selected_agent(e=e, agent=agent)
        self.agent_config_column.controls.append(agent_tile)
        attempt_to_update_control(self.agent_config_column)

    def display_selected_agent(self, e , agent: LocalAgent) -> None:
        self.display_agent_config_store(agent, e)
        show_selected_tile(e, self.agent_config_column)
        self.platform.page.update()

    # Replace placeholder with the individualized agent config store
    def display_agent_config_store(self, agent: LocalAgent, e) -> None:
        self.configure_agent_view.content = self.agent_config_section(agent)
        self.configure_agent_view.update()
        agent_specific_config_store = local_config_store.LocalConfigStoreManagerTab(
                                        self.platform.page,
                                        self.platform,
                                        agent
                                    ) 
        self._comprehensive_view.controls[1] = agent_specific_config_store.build_config_store_tab()
        self.platform.event_bus.publish("display_agent_config_manager")
        attempt_to_update_control(self._comprehensive_view)
        
    def add_agent(self, e) -> None:
        if self.agent_dropdown.value not in self.platform.added_agents and self.agent_dropdown.value is not None:
            self.forward_agent_appended(self.agent_dropdown.value)

    def build_agent_config_tab(self) -> Container:
        return self._comprehensive_view