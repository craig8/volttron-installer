# this page should allow you to potentially deploy multiple platforms
#  
import flet as ft
from flet import *

from typing import Callable

import logging

_log = logging.getLogger(__name__)

class Agent:
    def __init__(self):
        super().__init__()
        self.selected_column = Column()
        self.activity_colors = {
            "hovered_agent" : "red",
            "agent" : "green",
        }
        self.agent_tile = Container(
            width=175,
            height=100,
            border=border.all(4, self.activity_colors),
            content=Container()
        )
        pass
    
    def on_container_hover(e):
        #e.control.border = self.activity_colors['hovered_agent'] if e.data == "true" else self.activity_colors['agent']
        pass



def deploy_platform_view(page: Page) -> View:
    from volttron_installer.views import InstallerViews as vi_views
    from volttron_installer.components.program_card import ProgramTile, broooo_column
    
    # monolithic code; pressing button appends tile to main page
    def funny_func(e) -> None:
        broooo_column.controls.append(ProgramTile(page).build_card())
        print("please add a container")
        page.update()

    #validate the name field
    def validate_text(e) -> None:
        global _submit_
        valid_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
        input_text = e.control.value
        # Check if every character in the text is among the valid characters
        if all(c in valid_chars for c in input_text) and 0 <= len(input_text) <= 9:
            e.control.error_text = None  # Clear any previous error message
            _submit_ = True
        else:
            error_messages = []
            if not all(c in valid_chars for c in input_text):
                error_messages.append("Only letters, numbers, and underscores are allowed.")
            # if not (0 <= len(input_text) <= 9):
            #     error_messages.append("Length must be between 0 and 9 characters.")
            e.control.error_text = " ".join(error_messages)
            _submit_ = False
        #print(_submit_)
        e.control.update()
    
    # Container containing the form title and form input pair
    def field_pair(text, input) -> Container:
        return  Container(
            height=70,
            padding=padding.only(top=10,bottom=10, left=5,right=5),
            content=Row(
                controls=[
                    Container(
                        expand=2,
                        content=Text(f"{text}",size=20)
                    ),
                    Container(
                        expand=3,
                        content=input
                    )
                ],
                spacing=0
            )
        )

    def divide_fields(field_list) -> list:
        div = Divider(height=9, thickness=3, color="white")
        #puts a divider in between each field pair in the field list 
        return [element for pair in zip(field_list, [div] * (len(field_list) - 1)) for element in pair] + [field_list[-1], div]

    #name field
    name_field = TextField(
        hint_text="Only letters, numbers, and underscores are allowed.",
        on_change=validate_text
    )
    name_field_pair = field_pair("Name", name_field)

    #adress field
    all_addresses_checkbox = Checkbox(label="All Adresses")
    address_field = Container(content=all_addresses_checkbox)
    address_field_pair = field_pair("Adresses", address_field)

    #ports field
    ports_field = TextField()
    ports_field_pair = field_pair("Ports", ports_field)

    #bus field
    bus_field_pair = field_pair("Bus Type", Text("2mg", size= 18, color="white"))

    #all fields compiled and properlly managed
    all_field_pairs = [name_field_pair, address_field_pair, ports_field_pair, bus_field_pair]
    fields = divide_fields(all_field_pairs)
    
    #verify if the add platform form can be submitted whether or not the form fits the requirements
    _submit_ = True
    
    #agent column where the added agents will be stored
    agent_column = Column()



    #dummy options for testing
    def dropdown_change(e)-> None:
        if dd.value not in added_agents:
            added_agents.append(dd.value)
            print(added_agents)

    added_agents = []
    option1 = dropdown.Option(text="dummy1")
    option2 = dropdown.Option(text="dummy2")
    option3 = dropdown.Option(text="dummy3")
    dd = Dropdown(
        on_change=dropdown_change,
        options=[
            option1, option2, option3
        ]
    )

    
    return View(vi_views.deploy_platform.route, 
        [
            Stack(
                controls=[
                    ft.Container(
                        expand=True,
                        gradient=ft.RadialGradient(
                            colors=[ft.colors.PURPLE, ft.colors.BLACK],
                            radius=1.4,
                            center=ft.Alignment(0.8, 0.8)
                        )
                    ),
                    Column(
                        controls=[
                            Container( # header
                                #bgcolor="orange",
                                padding=padding.only(left=20,right=20),
                                content=Row(
                                    controls=[
                                        Text("Add Platform", size=60, color="white"),
                                        ElevatedButton(on_click= lambda _: page.go(vi_views.home.route)),
                                        ElevatedButton(on_click=funny_func) # CHANGE IN PRODUCTION
                                    ],
                                    alignment=MainAxisAlignment.SPACE_BETWEEN
                                )
                            ),
                            Container(
                                margin=margin.only(left=20,right=20),
                                bgcolor="#20f4f4f4",
                                expand=True,
                                #padding=padding.only(top=4),
                                border_radius=12,
                                content=Column( # parent column to house two other columns
                                    # how about we have a row return two columns, the left side can have containers with unifrom stying
                                    spacing=0,
                                    controls=[
                                        *fields,
                                        Container(
                                            expand=True,
                                            bgcolor="blue",
                                            content=Column(
                                                spacing=0,
                                                controls=[
                                                    Container(
                                                        height=70,
                                                        padding=padding.only(top=10,bottom=10, left=5,right=5),
                                                        bgcolor="red",
                                                        content=Row( # heading row will hold drop down and such
                                                            spacing=0,
                                                            controls=[
                                                                Container(
                                                                    bgcolor="green",
                                                                    expand=2,
                                                                    content=Text("Agents", size=20)
                                                                ),
                                                                Container(
                                                                    bgcolor="grey",
                                                                    expand=3,
                                                                    content=dd,
                                                                ),
                                                            ]
                                                        )
                                                    ),
                                                    Container(
                                                        expand=True,
                                                        content=Row(
                                                            spacing=0,
                                                            controls=[
                                                                Container(
                                                                    bgcolor="purple",
                                                                    expand=2,
                                                                    content=agent_column
                                                                ),
                                                                Container(
                                                                    expand=3
                                                                )
                                                            ]
                                                        ),
                                                    )
                                                ]
                                            )
                                        )
                                    ]
                                )
                            )
                        ],
                    ),
                ],
                expand=True
            )
        ],
    padding=0
    )