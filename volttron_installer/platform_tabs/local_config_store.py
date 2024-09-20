from volttron_installer.components.agent import Agent
from volttron_installer.components.base_tile import BaseTab, BaseTile
from volttron_installer.components.platform_components.platform import Platform
from volttron_installer.modules.remove_from_controls import remove_from_selection
from volttron_installer.modules.write_to_json import write_to_file
from volttron_installer.views import agent_setup
from volttron_installer.views.global_config_store import ConfigForm, Config
from flet import *
from volttron_installer.modules.styles import modal_styles2
from volttron_installer.modules.global_configs import agent_specific_configs, find_dict_index, global_agents, agent_specific_configs
from volttron_installer.modules.global_event_bus import global_event_bus
from dataclasses import dataclass
import asyncio

@dataclass
class LocalConfig(Config):
    # Basically just a copy of Config
    pass

class LocalConfigForm(ConfigForm):
    def __init__(self, config: LocalConfig, page: Page, current_agent: Agent, shared_platform: Platform):
        super().__init__(config, page)
        self.current_agent = current_agent
        self.platform = shared_platform

    async def save_config(self, e) -> None:
        old_name = self.config.name

        # Check if we are creating a new config, overwriting, or not overwriting
        check_overwrite: bool | None = await self.detect_conflict(agent_specific_configs[self.current_agent.agent_name]["config_store_entries"], self.name_field.value, self.config.name)
        
        if check_overwrite == True:
            global_event_bus.publish("soft_remove", self.config.tile.key)

        elif check_overwrite == False: 
            return

        # If no existing config with the same name, or if user chooses to overwrite
        self.config.type = self.view_type_radio_group.value
        
        content_data=self.content_value
        if self.config_mode == "json":
            content_data = self.clean_json_string(self.json_content_editor.value)
            content_data: dict = eval(content_data)

        elif self.config_mode == "csv":
            content_data=self.data_table_to_csv()
            self.config.content = str(content_data)

        self.config.name = self.name_field.value

        # agent_specific_configs[agent_index]["config_Store_entries"]
        # create a list[dict] out of the keys in config store entries
        # self.config.name : {}
        config_dictionary_appendable = {
                "type" : self.config.type,
                "content" : self.config.content
            }

        if check_overwrite == "rename":
            self.replace_key(agent_specific_configs[self.platform]["config_store_entries"][self.config.name], old_key=old_name, new_key=self.config.name)

        # Overwrites and/or appends a new config at the same time
        agent_specific_configs[self.platform]["config_store_entries"][self.config.name] = config_dictionary_appendable

        # Update the UI tile content
        self.config.tile.content.controls[0].value = self.config.name
        self.page.update()

        # Write the changes to file
        self.write_to_file("agent_specific_configs", agent_specific_configs)

class LocalConfigStoreManagerTab(BaseTab):
    def __init__(self, page: Page, shared_instance: Platform, agent: Agent) -> None:
        self.platform = shared_instance
        self.agent = agent
        self.working_agent_specific_configs = agent_specific_configs[self.platform.generated_url]

        self.platform.event_bus.subscribe("display_agent_config_manager", self.display_agent_config_manager)
        self.list_of_configs = Column(
            expand=2,
            controls=[
                Text(f"{self.agent.agent_name}'s drivers"),
                OutlinedButton(text="Setup a Config", on_click=self.add_new_config)
            ]
        )

        super().__init__(self.list_of_configs, page)
        self.page = page
        global_event_bus.subscribe("tab_change", self.tab_change)
        global_event_bus.subscribe("soft_remove", self.soft_remove)

    def display_agent_config_manager(self, data=None):
        self.tab_change()

    def add_new_config(self, e) -> None:
        self.add_new_tile(self.working_agent_specific_configs["config_store_entries"], "agent_specific_configs", LocalConfig, lambda instance, page: LocalConfigForm(instance, page, current_agent=self.agent, shared_platform = self.platform))
    
    def tab_change(self, selected_tab=None):
        self.refresh_tiles("agent_specific_configs", self.working_agent_specific_configs["config_store_entries"], LocalConfig, lambda instance, page: LocalConfigForm(instance, page, current_agent=self.agent, shared_platform = self.platform))

    # Need to rewrite remove_self function for our usecase
    def remove_self(self, global_lst: list, file_name: str, instance_attributes: dict):
        del agent_specific_configs[self.platform.generated_url]["config_store_entries"][instance_attributes["name"]]
        write_to_file(file_name, agent_specific_configs)
        remove_from_selection(self.instance_tile_column, instance_attributes["id"])
        self.tab.content.controls[2].content = Column(expand=3)
        self.page.update()
        global_event_bus.publish("update_global_ui", None)

    def build_config_store_tab(self) -> Container:
        return self.tab
