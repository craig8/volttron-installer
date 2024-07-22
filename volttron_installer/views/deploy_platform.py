# this page should allow you to potentially deploy multiple platforms
#  
from flet import *

from typing import Callable

import logging

_log = logging.getLogger(__name__)

def deploy_platform_view(page: Page) -> View:
    from volttron_installer.views import InstallerViews as vi_views
    from volttron_installer.components.program_card import ProgramTile, baka_column
    
    def funny_func(e):
        baka_column.controls.append(ProgramTile(page).build_card())
        print("please add a container")
        page.update()
    
    return View(vi_views.deploy_platform.route, 
        [
            Column(
                controls=[
                    Container( # header
                            bgcolor="orange",
                            padding=padding.only(left=20,right=20),
                            height=40,
                            content=Row(
                                controls=[
                                    Text("Deploy To Platform", size=30),
                                    ElevatedButton(on_click= lambda _: page.go(vi_views.home.route)),
                                    ElevatedButton(on_click=funny_func)
                                ],
                                alignment=MainAxisAlignment.SPACE_BETWEEN
                            )
                        )
                ]
            )
        ],
    padding=0
    )