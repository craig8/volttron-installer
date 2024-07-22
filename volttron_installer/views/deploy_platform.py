# this page should allow you to potentially deploy multiple platforms
#  
import flet as ft
from flet import *

from typing import Callable

import logging

_log = logging.getLogger(__name__)

def deploy_platform_view(page: Page) -> View:
    from volttron_installer.views import InstallerViews as vi_views
    from volttron_installer.components.program_card import ProgramTile, broooo_column
    
    def funny_func(e):
        broooo_column.controls.append(ProgramTile(page).build_card())
        print("please add a container")
        page.update()

    def validate_text(e):
        valid_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
        input_text = e.control.value
        # Check if every character in the text is among the valid characters
        if all(c in valid_chars for c in input_text) and 0 <= len(input_text) <= 9:
            e.control.error_text = None  # Clear any previous error message
        else:
            error_messages = []
            if not all(c in valid_chars for c in input_text):
                error_messages.append("Only letters, numbers, and underscores are allowed.")
            if not (0 <= len(input_text) <= 9):
                error_messages.append("Length must be between 0 and 9 characters.")
            e.control.error_text = " ".join(error_messages)
        
        e.control.update()

    name_field = TextField(
        label="Name",
        hint_text="max length: 9",
        on_change=validate_text
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
                                        ElevatedButton(on_click=funny_func)
                                    ],
                                    alignment=MainAxisAlignment.SPACE_BETWEEN
                                )
                            ),
                            Container(
                                margin=margin.only(left=20,right=20),
                                bgcolor="orange",
                                expand=True,
                                content=Row( # parent column to house two other columns
                                    controls=[
                                        Container(
                                            bgcolor="pink",
                                            expand=2,
                                        ),
                                        Container(
                                            bgcolor="yellow",
                                            expand=2,
                                        ),
                                    ]
                                )
                            )
                        ]
                    ),
                ],
                expand=True
            )
        ],
    padding=0
    )