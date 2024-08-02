# program_card.py

from flet import *
from volttron_installer.modules.dynamic_routes import dynamic_routes
from volttron_installer.components.background import gradial_background
from volttron_installer.components.Header import Header
from volttron_installer.platform_tabs.platform_config import PlatformConfig
from volttron_installer.components.program_components.program import Program, SiblingCommunicator

class ProgramTile(Program):
    def __init__(self, page: Page, container, generated_url: str, title: str, event_bus: SiblingCommunicator) -> None:
        super().__init__(title, page, generated_url, event_bus=event_bus)

        # Subscribe to events
        self.event_bus.subscribe("process_data", self.process_data)
        print(f"ProgramTile initialized. Activity state: {self.activity}, Object ID: {id(self)}")

        self.home_container = container
        self.program_tile = self.build_tile()

        self.name_field = TextField(hint_text="Only letters, numbers, and underscores are allowed.")
        self.all_addresses_checkbox = Checkbox(label="All Addresses")
        self.address_field = Container(content=self.all_addresses_checkbox)
        self.ports_field = TextField()
        self.submit_button = OutlinedButton("Submit", disabled=True)

        self.platform_config_tab = PlatformConfig(
            self.page,
            self.name_field,
            self.all_addresses_checkbox,
            self.ports_field,
            self.submit_button,
            self.event_bus,
            self.title,
            self.added_agents,
        ).platform_config_view()

        # Add route to dynamic routes dynamically
        view = self.program_view()
        dynamic_routes[self.generated_url] = view

    def specific_method(self):
        print("ProgramTile.specific_method called")
        # Implement specific action logic for ProgramTile

    def process_data(self, data):
        print("ProgramTile received:", data)
        eval(data)

    def get_background_color(self):
        return "#9d9d9d" if self.activity == "ON" else colors.with_opacity(0.65, "#9d9d9d")

    def get_text_color(self):
        return "white" if self.activity == "ON" else colors.with_opacity(0.65, "white")

    def get_status_color(self):
        return "#00ff00" if self.activity == "ON" else colors.with_opacity(0.65, "#ff0000")

    def update_program_tile_ui(self):
        print(f"ProgramTile update_program_tile_ui called. Program Object ID: {id(self)}, Activity: {self.activity}")
        # Update UI components based on activity state
        self.program_tile.bgcolor = self.get_background_color()
        self.program_tile.content.controls[0].controls[1].color = self.get_status_color()
        self.program_tile.content.controls[0].controls[1].value = self.activity
        for control in self.program_tile.content.controls:
            for subcontrol in control.controls:
                if isinstance(subcontrol, Text):
                    subcontrol.color = self.get_text_color()

    def build_tile(self):
        return Container(
            width=150,
            height=150,
            border_radius=25,
            padding=padding.all(10),
            bgcolor=self.get_background_color(),
            on_click=lambda e: self.page.go(self.generated_url),
            content=Column(
                controls=[
                    Row(controls=[Text(self.title, color=self.get_text_color()), Text(value=f"{self.activity}", color=self.get_status_color())]),
                    Row(controls=[Text("Agents"), Text("0")]),
                    Row(controls=[Text("Health"), Text("0")]),
                ]
            )
        )

    def build_card(self) -> Container:
        return self.program_tile

    def program_view(self) -> View:
        # Initializing the header and background
        header = Header(self.title, self.page, "/").return_header()
        background_gradient = gradial_background()
        return View(
            self.generated_url,
            controls=[
                Stack(
                    controls=[
                        background_gradient,
                        Column(
                            controls=[
                                header,
                                Tabs(
                                    selected_index=0,
                                    animation_duration=300,
                                    tabs=[
                                        Tab(
                                            text="Platform Config",
                                            content=self.platform_config_tab
                                        ),
                                        Tab(
                                            tab_content=Icon(icons.SEARCH),
                                            content=Text("This is Tab 2"),
                                        ),
                                        Tab(
                                            text="Tab 3",
                                            icon=icons.SETTINGS,
                                            content=Text("This is Tab 3"),
                                        ),
                                    ],
                                    expand=1,
                                )
                            ]
                        ),
                    ],
                    expand=True
                )
            ],
            padding=0
        )

# Container to hold program tiles
program_tile_container = Row(wrap=True)
