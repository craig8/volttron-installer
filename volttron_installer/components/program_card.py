"""
These objects should have the following properties:
    1. Recieve real time status updates such as health, on/off status, num of agents, any stopped agents
    2. Should route to their own unique page where additional modifications can be made

""" 
from flet import *
from volttron_installer.modules.dynamic_routes import dynamic_routes
from volttron_installer.components.background import gradial_background
from volttron_installer.components.Header import Header
from volttron_installer.platform_tabs.platform_config import PlatformConfig

class ProgramTile(UserControl): # full of monolithic code to see layout
    def __init__(self, page: Page, container, generated_url: str, title: str) -> None:
        super().__init__()
        self.title = title
        self.generated_url = f"/{generated_url}"
        self.home_container = container
        self.page = page
        self.activity = "OFF" # manually switched `ON`/`OFF` to see the visual
        self.colors = {
            "bgcolor": "#9d9d9d" if self.activity =="ON" else colors.with_opacity(0.65, "#9d9d9d"),
            "text_color": "white" if self.activity == "ON" else colors.with_opacity(0.65, "white"),
            "on_off": "#00ff00" if self.activity == "ON" else colors.with_opacity(0.65, "#ff0000")
        }
        self.program_tile = Container(
            width=150,
            height=150,
            border_radius=25,
            padding=padding.all(10),
            bgcolor=self.colors["bgcolor"],
            on_click=lambda e: self.page.go(self.generated_url), # will lead to individualized page for managing program, testing for now
            content=Column(
                controls=[
                    Row(controls=[Text(self.title, color=self.colors['text_color']), Text(value=f"{self.activity}", color=self.colors['on_off'])]),
                    Row(controls=[Text("Agents"), Text("0")]),
                    Row(controls=[Text("Health"), Text("0")]),
                ]
            )
        )

        # PLATFORM CONFIG SECITON
        self.name_field = TextField(hint_text="Only letters, numbers, and underscores are allowed.",)
        self.all_addresses_checkbox = Checkbox(label="All Adresses")
        self.address_field = Container(content=self.all_addresses_checkbox)
        self.ports_field = TextField()
        self.submit_button = OutlinedButton("Submit", disabled=True)
        #self, name_field, all_adresses_checkbox, ports_field, submit_button, page: Page, platform_title: str)
        self.platform_config_tab = PlatformConfig(self.name_field, self.address_field, self.ports_field, self.submit_button, self.page, self.title).platform_config_view()

        #add route to dynamic routes dynamically in a dynamic dynamically manner which is also dynamic
        view = self.program_view()
        dynamic_routes[self.generated_url] = view

    def build_card(self) -> Container:
        return self.program_tile
    
    def program_view(self) -> View:
        # Crude monolithinc way of doing it but its okay for now,
        # Initlializing the header and background
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
                                            content= self.platform_config_tab
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
            ]
        )

program_tile_container = Row(
    wrap=True
)