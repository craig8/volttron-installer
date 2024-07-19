from pydantic import BaseModel
from functools import partial

from .home import home_view
from .config_manager import config_manager_view
from .platforms import platforms_view

get_message_list = None
get_message = None


class _InstallerView(BaseModel):
    route: str
    instance: object


class _InstallerViews(BaseModel):
    home: _InstallerView = _InstallerView(route="/", instance=partial(home_view))
    config_manager: _InstallerView = _InstallerView(route="/config_manager",
                                                    instance=partial(
                                                        config_manager_view,
                                                        message="Woot this is a message sent"))
    platforms: _InstallerView = _InstallerView(route="/platforms",
                                                instance=partial(platforms_view))
    # sender: _InstallerView = _InstallerView(route="/sender",
    #                                 instance=partial(
    #                                     sender_view,
    #                                     get_certificates=get_certificates))
    # subscriber: _InstallerView = _InstallerView(route="/subscriber",
    #                                     instance=partial(
    #                                         subscriber_view,
    #                                         get_certificates=get_certificates))

    def __getitem__(self, item):
        return getattr(self, item)

    def __iter__(self):
        for page in self.__dict__.values():
            yield page


InstallerViews = _InstallerViews()


