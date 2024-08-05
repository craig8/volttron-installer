# home.py

import platform
from flet import *

from typing import Callable

import logging


_log = logging.getLogger(__name__)

import random
import string

# Empty list to keep track of platforms, using this list to avoid duplicate URLs
platforms_added = []

# Helper function to generate a random URL path
def generate_random_path(length=7) -> str:
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def generate_URL() -> str:
    while True:
        new_url = generate_random_path()
        if new_url not in platforms_added:
            platforms_added.append(new_url)
            print(platforms_added)
            return f"/{new_url}"    

def numerate_amount_of_platforms() -> str:
    platform_number = len(platforms_added)
    return f"P{platform_number + 1}"

def home_view(page: Page) -> View:
    from volttron_installer.views import InstallerViews as vi_views
    from volttron_installer.components.platform_tile import platform_tile_container
    from volttron_installer.components.background import gradial_background
    from volttron_installer.components.platform_tile import PlatformTile
    from volttron_installer.components.platform_components.Platform import create_sibling_communicator, Platform

    def add_platform_tile(e) -> None:
        event_bus = create_sibling_communicator()
        shared_platform_instance = Platform(numerate_amount_of_platforms(), page, generate_URL(), event_bus)
        platform_tile = PlatformTile(platform_tile_container, shared_platform_instance)
        platform_tile_container.controls.append(platform_tile.build_card())
        page.update()

    compybg = gradial_background()
    return View(
        "/",
        controls=[
            Stack(
                controls=[
                    compybg,
                    Column(
                        scroll=ScrollMode.AUTO,
                        controls=[
                            Container(  # header
                                padding=padding.only(left=20, right=20),
                                content=Row(
                                    controls=[
                                        Text("Overview", size=60, color="white"),
                                        IconButton(
                                            icon=icons.ADD,
                                            tooltip="Add platform",
                                            icon_color="white",
                                            icon_size=40,
                                            on_click=add_platform_tile
                                        ),
                                    ],
                                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                                ),
                            ),
                            Container(  # main view of all the platform tiles
                                padding=padding.only(left=15, right=0, top=50, bottom=15),
                                content=Column(
                                    scroll=ScrollMode.AUTO,
                                    controls=[platform_tile_container]
                                )
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
