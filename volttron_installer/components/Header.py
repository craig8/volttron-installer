from flet import *
from volttron_installer.modules.validate_field import validate_text

class Header:
    def __init__(self, title: str, page: Page, route: str):
        self.title: str = title
        self.page: Page = page
        self.route_back_to: str = route
        self.edit_mode: bool = False

        # establish editing logic for to flip flop between the two icons
        self.editing_icon = icons.EDIT

        self.delete_program_button = IconButton(icon=icons.DELETE, on_click=self.delete_thang)
        self.edit_program_title_button = IconButton(icon=self.editing_icon, on_click=self.handle_editing_mode)
        self.edit_delete_grouped = Container(content=Row(controls=[self.edit_program_title_button, self.delete_program_button]))

        # logic for the title editing functionality
        self.title_container = Container(visible=not self.edit_mode, content=Text(value=f"{self.title}", size=24))
        self.title_editing_field = TextField(value=self.title, visible=self.edit_mode, width=100, on_change=lambda e: validate_text(self.title_editing_field, self.edit_program_title_button))
        self.title_edit_container = Row(controls=[self.title_container, self.title_editing_field])

        self.header = Container(  # header
            padding=padding.only(left=20, right=20, top=20),
            content=Row(
                spacing=10,
                wrap=True,
                controls=[
                    Row(
                        controls=[
                            Row(
                                controls=[
                                    IconButton(
                                        icon=icons.ARROW_BACK_IOS_NEW,
                                        tooltip="Add platform",
                                        icon_color="white",
                                        icon_size=25,
                                        on_click=lambda e: self.page.go(self.route_back_to)
                                    ),
                                    self.title_edit_container
                                ]
                            ),
                            Container(
                                content=Row(
                                    controls=[self.edit_delete_grouped]
                                )
                            )
                        ]
                    ),
                ],
                alignment=MainAxisAlignment.SPACE_BETWEEN,
            ),
        )

    def delete_thang(self, e) -> None:
        print("You have deleted me how dare you!")

    def handle_editing_mode(self, e) -> None:
        # if we are in edit mode, that means the save button is active, so when we click, we are saving the title
        if self.edit_mode:
            self.title = self.title_editing_field.value
            self.title_container.content.value = self.title  # update the text value

        # flip the edit mode to true or false for the next time the edit button is clicked
        self.edit_mode = not self.edit_mode
        self.title_container.visible = not self.edit_mode
        self.title_editing_field.visible = self.edit_mode

        # update the editing icon
        self.edit_program_title_button.icon = icons.SAVE if self.edit_mode else icons.EDIT
        self.page.update()

    def return_header(self) -> Container:
        return self.header