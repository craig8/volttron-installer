# this page should allow you to potentially deploy multiple platforms
#  
from flet import *

from typing import Callable

import logging

_log = logging.getLogger(__name__)

def deploy_platform_view(page: Page) -> View:
    from volttron_installer.views import InstallerViews as vi_views

    return View(vi_views.deploy_platform.route, 
        [
            
        ],
    padding=0
    )