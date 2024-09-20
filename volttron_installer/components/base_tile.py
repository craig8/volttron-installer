from volttron_installer.modules.create_field_methods import divide_fields, field_pair
from volttron_installer.components.default_tile_styles import build_default_tile
from volttron_installer.modules.write_to_json import write_to_file, dump_to_var
from volttron_installer.modules.global_configs import find_dict_index
from volttron_installer.modules.global_event_bus import global_event_bus
from volttron_installer.modules.remove_from_controls import remove_from_selection
from volttron_installer.modules.attempt_to_update_control import attempt_to_update_control
from flet import *
from dataclasses import fields
import asyncio
from volttron_installer.modules.styles import modal_styles2

class BaseTile:
    counter = dump_to_var("tile_id")

    def __init__(self, title: str):
        self.title = title
        BaseTile.counter += 1
        write_to_file("tile_id", BaseTile.counter)

    def build_tile(self) -> Container:
        tile = build_default_tile(self.title)
        tile.key = f"container: {self.counter}"
        return tile
    
    def list_attributes(self):
        """Returns a list of the child class' attributes"""
        attributes = []
        for attribute_name in self.__dict__:
            attributes.append(attribute_name)
        return attributes


class BaseForm:
    def __init__(self, page: Page, form_fields: dict):
        self.page = page
        self.form_fields = form_fields
        self.val_constructor = []
        self.non_fields = []
        self.additional_content = [] # for anything special

        self.overwrite: bool = False

        for key, field in self.form_fields.items():
            if isinstance(field, TextField):
                self.val_constructor.append(field)
            else:
                self.classify_field(field)

        self.submit_button = OutlinedButton(text="Save", disabled=True, on_click=self.save_config)
        self.formatted_fields: any = self.create_fields()
        self._form = Column(
            #scroll=ScrollMode.ALWAYS,
            expand=3,
            controls=[
                *self.formatted_fields,
                self.submit_button,
                *self.additional_content
            ]
        )

    def classify_field(self, field):
        if hasattr(field, "key"):
            if field.key == "pass":
                self.additional_content.append(field)
            else:
                self.non_fields.append(field)
        else:
            self.non_fields.append(field)

    def refresh_form(self, instance: object) -> None:
        """Post init, will refresh form values"""
        instance_fields = fields(instance)
        instance_values = [getattr(instance, field_object.name) for field_object in instance_fields]
        for i, attribute in zip(self.val_constructor, instance_values):
            if isinstance(i, TextField):
                i.value = attribute
        self.page.update()

    def create_fields(self) -> list:
        """Pairs fields up with title then returns divided up field pairs."""
        field_pairs = []
        try:
            for obj, key in zip(self.val_constructor, self.form_fields.keys()):
                if obj == self.form_fields[key]:
                    field_pairs.append(field_pair(key, self.form_fields[key]))

            for i in list(self.form_fields.keys()):
                if self.form_fields[i] in self.non_fields:
                    field_pairs.append(field_pair(i, self.form_fields[i]))
            return divide_fields(field_pairs)
        except:
            print("form_fields contains unhashable kwargs")
            return None

    def validate_fields(self, e) -> None:
        # Implement field validation logic and toggle submit button state.
        valid: bool = all(field.value for field in self.val_constructor)
        self.toggle_submit_button(valid)

    async def save_config(self, e) -> None:
        # This method will be overwritten
        pass

    def toggle_submit_button(self, state: bool) -> None:
        self.submit_button.disabled = not state
        self.submit_button.update()

    def write_to_file(self, file: str, global_lst: list):
        write_to_file(file, global_lst)
    
    def replace_key(self, dictionary: dict, old_key: str, new_key: str):
        if old_key in dictionary:
            dictionary[new_key] = dictionary.pop(old_key)
            
    async def warning_modal(self, new_name: str) -> bool:
        loop = asyncio.get_event_loop()

        def no_overwrite(e):
            self.page.close(modal)
            self.overwrite = False
            loop.call_soon_threadsafe(future.set_result, False)

        def enable_overwrite(e):
            self.page.close(modal)
            self.overwrite = True
            loop.call_soon_threadsafe(future.set_result, True)

        modal_content = Column(
            alignment= alignment.center,
            controls=[
                Text("WARNING!", color="red", size=22),
                Text(f"You're about to overwrite a configuration named: {new_name}", size=18),
                Row(
                    alignment=MainAxisAlignment.SPACE_AROUND,
                    controls=[
                        OutlinedButton(content=Text("Cancel", color="red"), on_click=no_overwrite),
                        OutlinedButton(text="Overwrite", on_click=enable_overwrite)
                    ]
                )
            ]
        )

        modal = AlertDialog(
            modal=False,
            bgcolor="#00000000",
            content=Container(
                **modal_styles2(),
                width=400,
                height=170,
                content=modal_content
            )
        )

        # Create a future for the result
        future = loop.create_future()
        self.page.open(modal)
        await future
        return self.overwrite

    async def detect_conflict(self, working_dict: dict, item: str, old_name: str) -> bool | None | str:
        if old_name != item:
            return "rename" # We are just renaming the configuration, so we can return
        
        working_list = working_dict.keys()
        if item in working_list:
            overwrite_decision = await self.warning_modal(item)
            if overwrite_decision:
                return True
            else:
                return False
        else:
            return None # item was not found.
                
    def build_form(self) -> Column:
        return self._form

class BaseTab:
    def __init__(self, instance_tile_column: Column, page: Page):
        self.page = page
        self.instance_tile_column = instance_tile_column

        # Initialize column widths
        self.left_column_width = 200  # Initial width for the instance tile column
        self.right_column_width = page.width - self.left_column_width - 10  # Initial width for the form column
        
        self.left_instance_column: Container = Container(
                                        width=self.left_column_width,
                                        content=self.instance_tile_column
                                    )
        self.tab = self.build_base_tab()
        self.__post_init__()

    def __post_init__(self)->None:
        pass
        #self.left_instance_column.content.scroll=ScrollMode.ALWAYS

    def build_base_tab(self):
        # Initialize form container
        form_container = Container(width=self.right_column_width, content=Column(expand=3))

        def pan_update(e):
            # Perform the panning logic to adjust column widths
            self.left_column_width = max(200, self.left_column_width + e.delta_x)  # Set a minimum width of 50
            self.right_column_width = max(300, self.page.width - self.left_column_width - 10)  # Adjust the width of the right column

            # Update the dimensions of the container elements
            self.instance_tile_column.width = self.left_column_width
            form_container.width = self.right_column_width

            # Refresh the UI
            self.instance_tile_column.update()
            form_container.update()
            self.page.update()
        
        vertical_divider = GestureDetector(
            mouse_cursor=MouseCursor.RESIZE_COLUMN,
            content=VerticalDivider(
                width=3,
                thickness=3,
                color="white"
            ),
            on_pan_update=pan_update
        )

        tab_view = Container(
            height=900,
            padding=padding.only(left=10),
            margin=margin.only(left=10, right=10, bottom=5, top=5),
            bgcolor="#20f4f4f4",
            border_radius=12,
            content=Row(
                spacing=0,
                controls=[
                    self.instance_tile_column,
                    vertical_divider,
                    form_container
                ],
                expand=True
            )
        )
        return tab_view
 
    def refresh_tiles(self, file_name: str, global_dict: dict, instance_cls: type, instance_form_cls: type):
        if not self.contains_container():  # Checking if the container exists
            for key, item in global_dict.items():
                instance_cls_fields = fields(instance_cls)
                instance_cls_attributes = [attribute.name for attribute in instance_cls_fields if attribute.init]  # Only include attributes marked with init=True

                # Ensure the first attribute in 'instance_cls_attributes' gets the key's value
                instance_constructor = {attr: item.get(attr) for attr in instance_cls_attributes}
                if instance_cls_attributes:  # Ensure there is at least one attribute
                    first_attr = instance_cls_attributes[0]
                    instance_constructor[first_attr] = key

                # Create the instance with the constructor
                instance = instance_cls(**instance_constructor)

                # Extract instance_tile from the new instance
                instance_values = [getattr(instance, field.name) for field in instance_cls_fields]
                instance_tile: Container = instance_values[-1]

                # Create the form with the new instance
                form: BaseForm = instance_form_cls(instance, self.page)

                # Configure the new instance
                self.configure_new_instance(file_name, global_dict, instance_values, instance_tile, form, instance)

    def add_new_tile(self, global_list, file_name: str, object: BaseTile, form: BaseForm):
        field_objects = fields(object)
        attributes = [field_object.name for field_object in field_objects]
        object_constructor = {}
        for i, attribute in enumerate(attributes[:-1]):
            if i == 0:
                object_constructor[attribute] = "Configure Me!"
            else:
                object_constructor[attribute] = ""
        new_instance: BaseTile = object(**object_constructor)
        new_form = form(new_instance, self.page)

        new_instance_fields = fields(new_instance)
        new_instance_values = [getattr(new_instance, field_object.name) for field_object in new_instance_fields]
        new_tile: Container = new_instance_values[-1]

        self.configure_new_instance(file_name, global_list, new_instance_values, new_tile, new_form, new_instance)

    def configure_new_instance(self, file_name: str, global_list: list, instance_values, tile: Container, form: BaseForm, instance):
        tile.on_click =lambda e: self.show_selected_form(e, form)
        tile.content.controls[1].on_click = lambda e: self.remove_self(global_list, file_name, instance_attributes={"name" : instance_values[0], "id" : tile.key})
        self.instance_tile_column.controls.append(tile)
        attempt_to_update_control(self.instance_tile_column)
        form.refresh_form(instance)

    def contains_container(self):
        """Just checks if there is a container in the instance_tile_column"""
        for control in self.instance_tile_column.controls:
            if isinstance(control, Container):
                return True
        return False
    
    def soft_remove(self, key: str) -> None:
        """In the case of an over written config, we simply remove the tile from view
        as we can just use our old overwritten config 
        """
        remove_from_selection(self.instance_tile_column, key)
        self.tab.content.controls[2].content = Column(expand=3)
        self.page.update()
    
    def remove_self(self, global_lst: dict, file_name: str, instance_attributes: dict):
        if instance_attributes["name"] in global_lst.keys():
            del global_lst[instance_attributes["name"]]
        write_to_file(file_name, global_lst)
        remove_from_selection(self.instance_tile_column, instance_attributes["id"])
        self.tab.content.controls[2].content = Column(expand=3)
        self.page.update()
        global_event_bus.publish("update_global_ui", None)
    
    def show_selected_form(self, e, instance_form: BaseForm) -> None:
        self.tab.content.controls[2].content = instance_form.build_form()
        self.page.update()
        attempt_to_update_control(self.tab)
