import logging
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

import flet as ft
import flet.fastapi as flet_fastapi
from fastapi import FastAPI, Request
from flet import AppBar, Dropdown, ElevatedButton, Page, Text, View, colors, RouteChangeEvent

from .settings import get_settings

settings = get_settings()

logging.basicConfig(level=logging.getLevelName(settings.log_level))
logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
logging.getLogger("flet_core").setLevel(logging.WARNING)
logging.getLogger("flet.fastapi").setLevel(logging.WARNING)

_log = logging.getLogger(__name__)

os.environ["FLET_SECRET_KEY"] = settings.secret_key


async def main(page: Page):
    from volttron_installer.views import InstallerViews as vi_views
    page.theme_mode="dark"

    try:
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.title = settings.app_name

        def route_change(e: RouteChangeEvent):
            page.views.clear()

            for p in vi_views:
                if p.route == e.route:
                    page.views.append(p.instance(page=page))
                    break
            if not page.views:
                raise ValueError(f"The route {e.route} was not defined.")

            page.update()

        def view_pop(view):
            page.views.pop()
            top_view = page.views[-1]
            page.go(top_view.route)

        page.on_route_change = route_change
        page.on_view_pop = view_pop
        page.go(page.route)

    except Exception as e:
        _log.exception(e)


# Hook flet into FastAPI using flet.fastapi module
@asynccontextmanager
async def lifespan(app: FastAPI):
    await flet_fastapi.app_manager.start()
    yield
    await flet_fastapi.app_manager.shutdown()


# Create the fastapi app
app = FastAPI(lifespan=lifespan)

# Mount the flet app to the fastapi app.  More than one endpoint can be mounted to the same fastapi app.
app.mount(
    "/",
    flet_fastapi.app(main,
                     web_renderer=ft.WebRenderer.AUTO,
                     upload_dir=Path(
                         settings.upload_dir).expanduser().as_posix()))
