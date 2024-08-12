from dataclasses import dataclass
from volttron_installer.modules.styles import modal_styles
from volttron_installer.components.default_tile_styles import build_default_tile
from flet import *

@dataclass
class ConfigTile:
    """Config tile instance"""    
    name: str
    type: str
    content: str
    display_container: Container

    def build_config_tile(self) -> Container:
        config_tile = build_default_tile(self.name)

        config_tile.content.controls[1].on_click = self.delete_self
        config_tile.on_click = self.display_content
        return config_tile
    
    def delete_self(self, e):
        print("ConfigTile: this is just endless suffering please program me to delete myself")

    def display_content(self, e) -> None:
        config_content = Container(
                            content=Text(value=self.content, size=24)
                        )
        self.display_container.content = config_content
        self.display_container.update()

from volttron_installer.components.platform_components.platform import Platform

class ConfigStoreManager:
    def __init__(self, page: Page, platform_specific: any) -> None:
        self.page = page

        self.platform = platform_specific
        if isinstance(self.platform, Platform):
            self.platform.event_bus.subscribe("agent_is_selected", self.display_agent_specific)
        else:
            # activate function that displays global driver configs 
            pass

        self.name_field = TextField(color="black", label="Name", on_change=self.validate_submit)
        self.csv_radio = Radio(value="csv")
        self.json_radio = Radio(value="json")
        self.add_config_button = OutlinedButton(
                                    on_click=self.register_new_config,
                                    content=Text("Add", color="black"),
                                    disabled=True
                                )
        self.type_radio_group = RadioGroup(
            value="",
            on_change=self.validate_submit,
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
        self.config_content_view= Container(
                                    content=Text("Wow, so much content!")
                                )
        self.store_manager_view = Container(
            height=900,
            padding=padding.only(left=10),
            margin=margin.only(left=10, right=10, bottom=5, top=5),
            bgcolor="#20f4f4f4",
            border_radius=12,
            content=Row(
                controls=[
                    Container(
                        content=Column(
                            controls=[
                                OutlinedButton(
                                    text="Add a Configuration",
                                    on_click=lambda e: self.page.open(self.add_config_modal)
                                ),
                            ]
                        )
                    ),
                    VerticalDivider(color="white", width=9, thickness=3),
                    self.config_content_view
                ]
            )
        )

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

    def display_agent_specific(self):
        print("config store manager says wsg w gangalaunche")

    def validate_submit(self, e) -> None:
        if self.name_field.value and self.type_radio_group.value !="":
            self.add_config_button.disabled = False
        else:
            self.add_config_button.disabled = True
        self.add_config_button.update()

    def register_new_config(self, e) -> None:
        new_config = ConfigTile(name=self.name_field.value, type=self.type_radio_group.value, content=f"{self.name_field.value}'s content", display_container=self.config_content_view)
        append_to_container: list = self.store_manager_view.content.controls[0].content.controls
        tile_to_append = new_config.build_config_tile()
        append_to_container.append(tile_to_append)

        self.page.close(self.add_config_modal)
        self.store_manager_view.update()

    def build_store_view(self) -> Container:
        return self.store_manager_view
