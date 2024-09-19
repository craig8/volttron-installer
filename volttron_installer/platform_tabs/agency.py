from volttron_installer.components.agent import Agent
from volttron_installer.components.base_tile import BaseTab, BaseTile
from volttron_installer.components.platform_components.platform import Platform
from volttron_installer.modules.remove_from_controls import remove_from_selection
from volttron_installer.modules.write_to_json import write_to_file
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
    def __init__(self, config, page: Page, current_agent: Agent):
        super().__init__(config, page)
        self.current_agent = current_agent
        self.current_agent_index = find_dict_index(agent_specific_configs, self.current_agent.agent_name)

    async def warning_modal(self, new_name: str) -> bool:
        loop = asyncio.get_event_loop()

        def no_overwrite(e):
            self.page.close(modal)
            self.overwrite = False
            loop.call_soon_threadsafe(future.set_result, False)

        def enable_overwrite(e):
            self.page.close(modal)
            self.overwrite = True
            loop.call_soon_threadsafe(future.set_result, True)

        modal_content = Column(
            alignment= alignment.center,
            controls=[
                Text("WARNING!", color="red", size=22),
                Text(f"You're about to overwrite a driver named: {new_name}", size=18),
                Row(
                    alignment=MainAxisAlignment.SPACE_AROUND,
                    controls=[
                        OutlinedButton(content=Text("Cancel", color="red"), on_click=no_overwrite),
                        OutlinedButton(text="Overwrite", on_click=enable_overwrite)
                    ]
                )
            ]
        )

        modal = AlertDialog(
            modal=False,
            bgcolor="#00000000",
            content=Container(
                **modal_styles2(),
                width=400,
                height=170,
                content=modal_content
            )
        )

        # Create a future for the result
        future = loop.create_future()
        self.page.open(modal)
        await future
        return self.overwrite

    async def save_config(self, e) -> None:

        #agent names are stored within the first kwarg
        for config_name in agent_specific_configs[self.current_agent_index]["config_store_entries"].keys():
            if config_name == self.name_field.value:
                overwrite_decision = await self.warning_modal(self.name_field.value)
                if overwrite_decision:
                    global_event_bus.publish("soft_remove", self.config.tile.key)
                    break # break out of for loop because user chose to overwrite
                else:
                    return  # Cancel saving process if user decides not to overwrite the config

        # If no existing config with the same name, or if user chooses to overwrite
        self.config.type = self.view_type_radio_group.value
        
        content_data=self.content_value
        if self.config_mode == "JSON":
            content_data = self.clean_json_string(self.json_content_editor.value)
            print(content_data)
            content_data: dict = eval(content_data)

        elif self.config_mode == "CSV":
            content_data=self.data_table_to_csv()

        self.config.content = str(content_data)

        old_config_name = self.config.name
        if self.config.name == "Configure Me!":
            old_config_name = self.name_field.value # if it was a placeholder name, allows newly formed configs to overwrite old configs

        self.config.name = self.name_field.value

        # agent_specific_configs[agent_index]["config_Store_entries"]
        # create a list[dict] out of the keys in config store entries
        current_agent_config_store_entries = [{"name" : key} for key in agent_specific_configs[self.current_agent_index]["config_store_entries"].keys()]
        config_index = find_dict_index(current_agent_config_store_entries, old_config_name)
        # self.config.name : {}
        config_dictionary_appendable = {
                "type" : self.config.type,
                "content" : self.config.content
            }

        # Overwrites and/or appends a new config at the same time
        agent_specific_configs[self.current_agent_index]["config_store_entries"][self.config.name] = config_dictionary_appendable

        # Update the UI tile content
        self.config.tile.content.controls[0].value = self.config.name
        self.page.update()

        # Write the changes to file
        self.write_to_file("agent_specific_configs", agent_specific_configs)

class LocalConfigStoreManagerTab(BaseTab):
    def __init__(self, page: Page, shared_instance: Platform, agent: Agent) -> None:
        self.platform = shared_instance
        self.agent = agent
        self.agent_index = find_dict_index(agent_specific_configs, self.agent.agent_name)
        
        self.agent_drivers: list[dict] # default to empty list[dict]
        for agent_dict in agent_specific_configs:
            if agent_dict["agent_name"] == self.agent.agent_name:
                # If we find a match, we begin the process of gathering all 
                # configs and arranging them into list[dict] for an already
                # existing parcing structure
                self.agent_drivers = []
                for key in agent_dict["config_store_entries"].keys():
                    agent_appendable = {}
                    agent_appendable["name"] = key
                    agent_appendable["type"] = agent_dict["config_store_entries"][key]["type"]
                    agent_appendable["content"] = agent_dict["config_store_entries"][key]["content"]
                    self.agent_drivers.append(agent_appendable)
                break # once we find our match, we stop iterating.

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
        self.add_new_tile(self.agent_drivers, "agent_specific_configs", LocalConfig, lambda instance, page: LocalConfigForm(instance, page, current_agent=self.agent))
    
    def tab_change(self, selected_tab=None):
        self.refresh_tiles("agent_specific_configs", self.agent_drivers, LocalConfig, lambda instance, page: LocalConfigForm(instance, page, current_agent=self.agent))

    # Need to rewrite remove_self function for our usecase
    def remove_self(self, global_lst: list, file_name: str, instance_attributes: dict):
        index = find_dict_index(global_lst, instance_attributes["name"])
        if index is not None:
            del agent_specific_configs[self.agent_index]["config_store_entries"][instance_attributes["name"]]
            write_to_file(file_name, agent_specific_configs)
        else:
            print("The instance you are trying to remove hasn't been properly registered yet. It has been removed")
        remove_from_selection(self.instance_tile_column, instance_attributes["id"])
        self.tab.content.controls[2].content = Column(expand=3)
        self.page.update()
        global_event_bus.publish("update_global_ui", None)

    def build_config_store_tab(self) -> Container:
        return self.tab
