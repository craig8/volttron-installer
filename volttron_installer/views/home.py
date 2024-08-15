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

# Generates until URL is unique
def generate_URL() -> str:
    while True:
        new_url = generate_random_path()
        generated_url = f"/{new_url}"
        if generated_url not in platforms_added:
            platforms_added.append(generated_url)
            return generated_url

def numerate_amount_of_platforms() -> str:
    platform_number = len(platforms_added)
    return f"P{platform_number + 1}"

def home_view(page: Page) -> View:
    from volttron_installer.views import InstallerViews as vi_views
    from volttron_installer.views import agent_setup, hosts_tab, global_config_store
    from volttron_installer.components.platform_tile import platform_tile_container
    from volttron_installer.components.background import gradial_background
    from volttron_installer.components.platform_tile import PlatformTile
    from volttron_installer.components.platform_components.platform import create_sibling_communicator, Platform
    def add_platform_tile(e) -> None:
        # Creats a singal isntance of ObjectCommunicator to be used throughout the whole platform
        event_bus = create_sibling_communicator()
        
        # Creates a shared platform instance with that same ObjectCommunicator
        shared_platform_instance = Platform(numerate_amount_of_platforms(), page, generate_URL(), event_bus)
        platform_tile = PlatformTile(platform_tile_container, shared_platform_instance)
        
        # Add platform tile to container
        platform_tile_container.controls.append(platform_tile.build_card())
        page.update()

        # Change the selected index of the tabs to 0
        tabs_reference.selected_index = 0
        tabs_reference.update()

    # Initialize tabs
    agent_setup_tab = agent_setup.AgentSetupTab(page).build_agent_setup_tab()
    host_config_tab = hosts_tab.HostTab(page).build_hosts_tab()
    config_store_tab = global_config_store.ConfigStoreManager(page, False).build_store_view()

    background_gradient = gradial_background()

    # Create the view and Tabs while assigning a reference
    tabs_reference = Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            Tab(
                text="Platforms",
                content=Container(  # main view of all the platform tiles
                    padding=padding.only(left=15, right=0, top=50, bottom=15),
                    content=Column(
                        scroll=ScrollMode.AUTO,
                        controls=[platform_tile_container]
                    )
                )
            ),
            Tab(
                text="Agent Setup",
                content=agent_setup_tab
            ),
            Tab(
                text="Hosts",
                content=host_config_tab
            ),
            Tab(
                text="Config Store Manager",
                content=config_store_tab
            )
        ],
        expand=1
    )

    view = View(
        "/",
        controls=[
            Stack(
                controls=[
                    background_gradient,
                    Column(
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
                            tabs_reference
                        ],
                        expand=True
                    ),
                ],
                expand=True
            )
        ],
        padding=0
    )
    return view