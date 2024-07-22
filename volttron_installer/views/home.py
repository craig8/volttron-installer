import flet as ft
from flet import *

from typing import Callable

import logging

_log = logging.getLogger(__name__)


def home_view(page: Page) -> View:
    from volttron_installer.views import InstallerViews as vi_views

    return View("/", [
        Column(
            controls=[
                Container( # header
                    bgcolor="blue",
                    padding=padding.only(left=20, right=20),
                    content=Row(
                        controls=[
                            Text("Overview", size=30),
                            IconButton(icon=icons.ADD,
                                       tooltip="Add platform",
                                       on_click=lambda _: page.go(vi_views.deploy_platform.route)),
                            ElevatedButton("Platform List", on_click=lambda _: page.go(vi_views.platform_manager.route)),
                        ],
                        alignment=MainAxisAlignment.SPACE_BETWEEN,
                    )
                ),
                Container( # main view of all the program tiles
                    bgcolor="orange",
                    padding=padding.only(left=50, right=50),
                    #expand=True,
                    #content= platform_container_column 
                )
            ]
        ),
        # AppBar(title=Text("Choose Application"),
        #        automatically_imply_leading=False,
        #        #bgcolor=colors.SURFACE_VARIANT),
        # ElevatedButton("Configuration Manager", on_click=lambda _: page.go(vi_views.config_manager.route)),
        # ElevatedButton("Platform List",
        #                on_click=lambda _: page.go(vi_views.platform_manager.route)),
    ],
    padding=0
    )

# add containers for the amount of platforms that have been added, could be added in
# a form of objects or what not

# if home page is going to be the overview page, maybe have each of these objects route to
# their own `platform_manager.py`?
