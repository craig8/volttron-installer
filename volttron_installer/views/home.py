import flet as ft
from flet import *

from typing import Callable

import logging

_log = logging.getLogger(__name__)


def home_view(page: Page) -> View:
    from volttron_installer.views import InstallerViews as vi_views
    from volttron_installer.components.program_card import broooo_column
    
    return ft.View(
        "/",
        controls=[
            ft.Stack(
                controls=[
                    ft.Container(
                        expand=True,
                        gradient=ft.RadialGradient(
                            colors=[ft.colors.PURPLE, ft.colors.BLACK],
                            radius=1.4,
                            center=ft.Alignment(0.8, 0.8)
                        )
                    ),
                    ft.Column(
                        controls=[
                            ft.Container(  # header
                                #bgcolor="blue",
                                padding=ft.padding.only(left=20, right=20),
                                content=ft.Row(
                                    controls=[
                                        ft.Text("Overview", size=60, color="white"),
                                        ft.IconButton(
                                            icon=ft.icons.ADD,
                                            tooltip="Add platform",
                                            icon_color="white",
                                            icon_size=40,
                                            on_click=lambda _: page.go(vi_views.deploy_platform.route)
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                ),
                            ),
                            ft.Container(  # main view of all the program tiles
                                #bgcolor="#000000",
                                padding=ft.padding.only(left=50, right=0, top=50),
                                expand=True,
                                content=broooo_column,
                            ),
                        ],
                        expand=True
                    ),
                ],
                expand=True
            ),
        ],
        padding=0
    )
# add containers for the amount of platforms that have been added, could be added in
# a form of objects or what not

# if home page is going to be the overview page, maybe have each of these objects route to
# their own `platform_manager.py`?
