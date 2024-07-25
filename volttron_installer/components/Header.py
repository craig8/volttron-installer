# One problem wit hthis configuration is that if the title is too long, its bad; same with the home view header

from flet import *

class Header:
    def __init__(self, title, page, route):
        self.title = title
        self.page = page
        self.route_back_to = route
        self.header = Container(  # header
            padding=padding.only(left=20, right=20),
            content=Row(
                wrap=True,
                controls=[
                    IconButton(
                        icon=icons.ARROW_BACK_IOS_NEW,
                        tooltip="Add platform",
                        icon_color="white",
                        icon_size=40,
                        on_click=lambda e: self.page.go(self.route_back_to)
                    ),
                    Text(self.title, size=60, color="white"),
                ],
                alignment=MainAxisAlignment.SPACE_BETWEEN,
            ),
        )

    def return_header(self) -> Container:
        return self.header 