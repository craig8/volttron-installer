# One problem wit hthis configuration is that if the title is too long, its bad; same with the home view header

from flet import *

class Header:
    def __init__(self, title: str, page:Page, route: str):
        self.title: str = title
        self.page: Page = page
        self.route_back_to: str = route
        self.edit_mode: bool = False

        # logic for the title editing functionality
        self.title_container = Container(visible= not self.edit_mode, content=Text(value=f"{self.title}"))
        self.title_editing_field = TextField(value=f"{self.title}", visible=self.edit_mode)
        self.title_edit_container = Row(controls=[self.title_container, self.title_editing_field])

        # establish editing logic for to flip flop between the two icons 
        self.editing_icons = {
            "icon" : icons.EDIT if self.edit_mode == False else icons.SAVE,
            "color" : "white"
        }
        self.delete_program_button = IconButton(icon=icons.DELETE, on_click=self.delete_thang())
        self.edit_program_title_button = IconButton(icon=self.editing_icons['icon'], on_click=self.handle_editing_mode())
        self.edit_delete_grouped = Container(content=Row(controls=[self.edit_program_title_button, self.delete_program_button]))

        self.header = Container(  # header
            padding=padding.only(left=20, right=20),
            content=Row(
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

    def delete_thang(self) -> None:
        print("You have deleted me how dare you!")

    def handle_editing_mode(self) -> None:
        # if we are in edit mode, that means the save button is active so when we click, we are saving the title
        if self.edit_mode:
            self.title = self.title_editing_field.value
            self.title_container.value = self.title

        # flip the edit mode to true or false for the next time the edit button is clicked
        self.edit_mode = not self.edit_mode
        self.title_container.visible = not self.edit_mode
        self.title_editing_field.visible = self.edit_mode
        self.edit_program_title_button.icon = self.editing_icons
        self.page.update()

    def return_header(self) -> Container:
        return self.header 