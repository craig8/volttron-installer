"""
Module to manage the header section of the platform management application using the Flet framework.
"""

from flet import *
from volttron_installer.modules.validate_field import validate_text
from volttron_installer.components.platform_components.platform import Platform

class Header:
    """
    Class to represent and manage the header section of the platform management application.

    Attributes:
        shared_instance (Platform): Shared instance of the Platform class containing platform information.
        submit_button (OutlinedButton): The button used to deploy the platform.
        route (str): The route to go back to on clicking the back button.
    """
    def __init__(self, shared_instance, submit_button: OutlinedButton, route: str):
        """
        Initialize a Header instance.

        Args:
            shared_instance (Platform): Shared instance of the Platform class.
            submit_button (OutlinedButton): Button to deploy the platform.
            route (str): Route to go back to on clicking the back button. (Will probably
                         forever be `/` but its future proofed at least!!)
        """
        self.platform: Platform = shared_instance
        self.route_back_to: str = route
        self.edit_mode: bool = False

        self.deploy_button = submit_button
        self.deploy_button.on_click = self.deploy_platform

        # Subscribe to platform events
        self.platform.event_bus.subscribe("deploy_button_update", self.adjust_submit_validity)

        # Initialize editing logic for button icons
        self.editing_icon = icons.EDIT

        self.delete_program_button = IconButton(icon=icons.DELETE, on_click=self.delete_platform)
        self.edit_program_title_button = IconButton(icon=self.editing_icon, on_click=self.handle_editing_mode)
        self.edit_delete_grouped = Container(content=Row(controls=[self.edit_program_title_button, self.delete_program_button]))

        # Logic for the title editing functionality
        self.title_container = Container(visible=not self.edit_mode, content=Text(value=f"{self.platform.title}", size=24))
        self.title_editing_field = TextField(
            value=self.platform.title, 
            visible=self.edit_mode,
            width=100, 
            on_change=lambda e: validate_text(self.title_editing_field, self.edit_program_title_button)
        )
        self.title_edit_container = Row(controls=[self.title_container, self.title_editing_field], wrap=True)

        self.header = Container(
            padding=padding.only(left=20, right=20, top=20),
            content=Row(
                spacing=10,
                wrap=True,
                controls=[
                    Row(
                        controls=[
                            IconButton(
                                icon=icons.ARROW_BACK_IOS_NEW,
                                tooltip="Add platform",
                                icon_color="white",
                                icon_size=25,
                                on_click=lambda e: self.platform.page.go(self.route_back_to)
                            ),
                            self.title_edit_container
                        ]
                    ),
                    Container(
                        content=Row(
                            controls=[self.edit_delete_grouped, self.deploy_button]
                        )
                    )
                ],
                alignment=MainAxisAlignment.SPACE_BETWEEN,
            ),
        )

    def deploy_platform(self, e) -> None:
        """
        Handle the platform deployment event.

        Args:
            e: The event object.
        """
        print("Header: everyone update their UI!")
        self.platform.flip_activity()

        # Make platformTile push all data entries into the shared instance
        self.platform.event_bus.publish("deploy_all_data", "self.submit_fields()")
        self.platform.page.update()
        self.header.update()
    
    def adjust_submit_validity(self, state: bool):
        """
        Adjust the validity of the submit button.

        Args:
            state (bool): The state to set for the submit button's disabled property.
        """
        self.deploy_button.disabled = state
        self.deploy_button.update()

    def deploy_to_platform(self, e) -> None:
        """
        Deploy to the platform.

        Args:
            e: The event object.
        """
        self.platform.flip_activity()

        # Tell PlatformTile to update their UI after submission
        self.platform.event_bus.publish('process_data', "self.update_platform_tile_ui()")

    def delete_platform(self, e) -> None:
        """
        Handle the delete button click event.

        Args:
            e: The event object.
        """
        print("You have deleted me how dare you!")

    def handle_editing_mode(self, e) -> None:
        """
        Handle the editing mode for the title.

        Args:
            e: The event object.
        """
        if self.edit_mode:
            self.title = self.title_editing_field.value
            self.title_container.content.value = self.title  # Update the text value

        self.edit_mode = not self.edit_mode
        self.title_container.visible = not self.edit_mode
        self.title_editing_field.visible = self.edit_mode

        # Update the editing icon
        self.edit_program_title_button.icon = icons.SAVE if self.edit_mode else icons.EDIT
        self.platform.page.update()

    def return_header(self) -> Container:
        """
        Return the header container.
        """
        return self.header
