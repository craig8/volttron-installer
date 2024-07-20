from flet import AppBar, ElevatedButton, Page, Text, View, colors

from typing import Callable

import logging

_log = logging.getLogger(__name__)


def home_view(page: Page) -> View:
    from volttron_installer.views import InstallerViews as vi_views

    return View("/", [
        AppBar(title=Text("Choose Application"),
               automatically_imply_leading=False,
               bgcolor=colors.SURFACE_VARIANT),
        ElevatedButton("Configuration Manager", on_click=lambda _: page.go(vi_views.config_manager.route)),
        ElevatedButton("Platform List",
                       on_click=lambda _: page.go(vi_views.platform_manager.route)),
    ])
# add containers for the amount of platforms that have been added, could be added in
# a form of objects or what not

# if home page is going to be the overview page, maybe have each of these objects route to
# their own `platform_manager.py`?
