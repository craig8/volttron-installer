from volttron_installer.modules.create_field_methods import divide_fields, field_pair
from volttron_installer.components.default_tile_styles import build_default_tile
from volttron_installer.modules.write_to_json import write_to_file, dump_to_var
from volttron_installer.modules.global_configs import find_dict_index
from volttron_installer.modules.global_event_bus import global_event_bus
from volttron_installer.modules.remove_from_controls import remove_from_selection
from flet import *
from dataclasses import fields

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
        """Pairs fields up with title then returns divided up field pairs"""
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

    def save_config(self, e) -> None:
        # This method will be overwritten
        pass

    def toggle_submit_button(self, state: bool) -> None:
        self.submit_button.disabled = not state
        self.submit_button.update()

    def write_to_file(self, file: str, global_lst: list):
        write_to_file(file, global_lst)

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
        
    def refresh_tiles(self, file_name: str, global_list: list, instance_cls: object, instance_form_cls: object):
        if self.contains_container() == False:
            for item in global_list:
                instance_cls_field = fields(instance_cls)
                instance_cls_attributes = [attribute.name for attribute in instance_cls_field]
                instance_constructor = {}
                for attribute, key in zip(item, instance_cls_attributes):
                    instance_constructor[key] = item[key]
    
                # Create instance with our constructor
                instance = instance_cls(**instance_constructor)
                
                # Create a new field out of our new instance, extract instance_tile
                instance_fields = fields(instance)
                instance_values = [getattr(instance, field_object.name) for field_object in instance_fields]
                instance_tile: Container = instance_values[-1]

                # Create form with our new instance
                form: BaseForm = instance_form_cls(instance, self.page)

                self.configure_new_instance(file_name, global_list, instance_values, instance_tile, form, instance)

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
        tile.content.controls[1].on_click = lambda e: self.remove_self(global_list, file_name, {"name" : instance_values[0], "id" : tile.key})
        self.instance_tile_column.controls.append(tile)
        self.instance_tile_column.update()
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
        self.tab.content.controls[2] = Column(expand=3)
        self.page.update()
    
    def remove_self(self, global_lst: list, file_name: str, instance_attributes: dict):
        index = find_dict_index(global_lst, instance_attributes["name"])
        if index is not None:
            global_lst.pop(index)
            write_to_file(file_name, global_lst)
        else:
            print("The instance you are trying to remove hasn't been properly registered yet. It has been removed")
        remove_from_selection(self.instance_tile_column, instance_attributes["id"])
        self.tab.content.controls[2] = Column(expand=3)
        self.page.update()
        global_event_bus.publish("update_global_ui", None)
    
    def show_selected_form(self, e, instance_form: BaseForm) -> None:
        print("I should be showing a form dude")
        self.tab.content.controls[2].content = instance_form.build_form()
        self.page.update()
