from volttron_installer.components.base_tile import BaseForm, BaseTab, BaseTile
from flet import *
from volttron_installer.modules.global_configs import global_drivers, find_dict_index
from volttron_installer.modules.validate_field import check_csv_field, check_json_field
from volttron_installer.modules.global_event_bus import global_event_bus
from dataclasses import dataclass, field
import json

# Constants
key_constructor = [
    "name",
    "content",
    "type",
]

@dataclass
class Config(BaseTile):
    name: str
    content: str
    type: str  # CSV or JSON

    tile: Container = field(init=False)

    def __post_init__(self):
        super().__init__(self.name)  # Initialize BaseTile with name
        self.tile = self.build_config_tile()

    def build_config_tile(self) -> Container:
        return self.build_tile()  # Calls BaseTile's build_tile method

class ConfigForm(BaseForm):
    def __init__(self, config, page: Page):
        self.name_field = TextField(on_change=self.validate_fields)
        self.type_radio_group = RadioGroup(
            value="",
            on_change=self.type_change,
            content=Row(
                spacing=25,
                controls=[
                    Radio(label="JSON", value="JSON"),
                    Radio(label="CSV", value="CSV")
                ]
            )
        )
        self.content_field = TextField(on_change=self.validate_fields)

        form_fields = {
            "Name": self.name_field,
            "Content": self.content_field,
            "Type": self.type_radio_group,
        }

        super().__init__(page, form_fields)
        self.config: Config = config
        self.config_mode = None
        self.content_field_validity = False
        self.submit = False

    def validate_fields(self, e) -> None:
        fields = [self.form_fields[i].value for i in self.form_fields.keys() if i != "Type"]
        all_fields_valid = all(fields)

        content_valid = self.correct_input() is not False

        if all_fields_valid and content_valid and self.submit:
            self.toggle_submit_button(True)  # Enable button if all fields are valid
        else:
            self.toggle_submit_button(False)  # Disable button if any field is not valid

    def correct_input(self) -> bool:
        if self.config_mode == "CSV":
            return check_csv_field(self.content_field)
        elif self.config_mode == "JSON":
            return check_json_field(self.content_field)
        else:
            print("You need to select your type of field")

    def type_change(self, e):
        self.config_mode = e.control.value
        self.submit = True
        self.validate_fields(e)

    def save_config(self, e) -> None:
        # Update the config object with current values from the fields
        self.config.name = self.name_field.value
        self.config.type = self.type_radio_group.value
        self.config.content = self.content_field.value

        old_name = self.config.name
        index = find_dict_index(global_drivers, old_name)

        config_dictionary_appendable = {
            "name": self.config.name,
            "type": self.config.type,
            "content": self.config.content,
        }

        # If an existing entry already exists
        if index is not None:
            # Update the existing entry
            global_drivers[index] = config_dictionary_appendable
        else:
            # Add a new entry
            global_drivers.append(config_dictionary_appendable)

        # Update the UI tile content
        self.config.tile.content.controls[0].value = self.config.name
        self.page.update()
        
        # Write the changes to file
        self.write_to_file("drivers", global_drivers)

class ConfigStoreManagerTab(BaseTab):
    def __init__(self, page: Page) -> None:
        self.list_of_configs = Column(
            expand=2,
            controls=[
                OutlinedButton(text="Setup a Config", on_click=self.add_new_config)
            ]
        )

        super().__init__(self.list_of_configs, page)
        self.page = page
        global_event_bus.subscribe("tab_change", self.tab_change)

    def add_new_config(self, e) -> None:
        self.add_new_tile(global_drivers, "drivers", Config, ConfigForm)

    def tab_change(self, selected_tab):
        self.refresh_tiles("drivers", global_drivers, Config, ConfigForm)

    def build_config_store_tab(self) -> Container:
        return self.tab
