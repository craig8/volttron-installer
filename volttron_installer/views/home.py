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
    # While loop keeps generating a new URL until its unique
    while True:
        # Generate unique URL math
        new_url = generate_random_path()
        # If URL is not in platforms_added, add it and return the new URL
        if new_url not in platforms_added:
            platforms_added.append(new_url)
            print(platforms_added)
            return f"/{new_url}"

def numerate_amount_of_platforms() -> int:
    platform_number = len(platforms_added)
    return f"P{platform_number}"

def home_view(page: Page) -> View:
    from volttron_installer.views import InstallerViews as vi_views
    from volttron_installer.components.program_card import program_tile_container
    from volttron_installer.components.background import gradial_background
    from volttron_installer.components.program_card import ProgramTile

    # on tile click, generate a new object and append it to the column containing the tiles
    def add_platform_tile(e) -> None:
        program_tile_container.controls.append(ProgramTile(page, program_tile_container, generate_URL(), numerate_amount_of_platforms()).build_card())
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
                            Container(  # main view of all the program tiles
                                padding=padding.only(left=15, right=0, top=50, bottom=15),
                                content=Column( # column to enable scrolling if necessary
                                    scroll=ScrollMode.AUTO,
                                    controls=[program_tile_container]
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
# add containers for the amount of platforms that have been added, could be added in
# a form of objects or what not

# if home page is going to be the overview page, maybe have each of these objects route to
# their own `platform_manager.py`?
