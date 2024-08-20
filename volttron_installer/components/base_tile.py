from volttron_installer.modules.create_field_methods import divide_fields, field_pair
from volttron_installer.components.default_tile_styles import build_default_tile
from volttron_installer.modules.write_to_json import write_to_file
from volttron_installer.modules.global_configs import find_dict_index
from volttron_installer.modules.global_event_bus import global_event_bus
from volttron_installer.modules.remove_from_controls import remove_from_selection
from flet import *

class BaseTile:
    counter = 0

    def __init__(self, title: str):
        self.title = title
        BaseTile.counter += 1

    def build_tile(self) -> Container:
        tile = build_default_tile(self.title)
        tile.key = f"container: {self.counter}"
        return tile


class BaseForm:
    def __init__(self, page: Page, form_fields: dict):
        self.page = page
        self.form_fields = form_fields
        self.val_constructor = []
        try:
            self.val_constructor: list= [form_fields[i] for i in form_fields.keys()]
        except:
            raise ValueError("base_tile reads form fields as unhashable")
        self.submit_button = OutlinedButton(text="Save", disabled=True, on_click=self.save_config)
        self.formatted_fields: any = self.create_fields()
        self._form = Column(
            expand=3,
            controls=[
                *self.formatted_fields,
                self.submit_button,
            ]
        )

    def create_fields(self) -> list:
        """Pairs fields up with title then returns divided up field pairs"""
        field_pairs = []
        try:
            for i in self.form_fields.keys():
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
    def __init__(self, controls_lst: list, page: Page):
        self.page = page
        self.controls_lst = controls_lst
        self.tab = self.build_base_tab(Column(expand=3))

    def build_base_tab(self, form: Control):
        tab_view = Container(
            height=900,
            padding=padding.only(left=10),
            margin=margin.only(left=10, right=10, bottom=5, top=5),
            bgcolor="#20f4f4f4",
            border_radius=12,
            content=Row(
                spacing=0,
                controls=[
                    self.controls_lst,
                    VerticalDivider(color="white", width=3, thickness=3),
                    form
                ]
            )
        )
        return tab_view

    def remove_self(self, global_lst: list, file_name: str, instance_attributes: dict):
        index = find_dict_index(global_lst, instance_attributes["name"])
        if index is not None:
            global_lst.pop(index)
            write_to_file(file_name, global_lst)
        else:
            print("The instance you are trying to remove hasn't been properly registered yet.")
        remove_from_selection(self.controls_lst, instance_attributes["id"])
        self.tab.content.controls[2] = Column(expand=3)
        self.page.update()
        global_event_bus.publish("update_global_ui", None)
    
    def show_selected_form(self, e, instance_form: BaseForm) -> None:
        self.tab.content.controls[2] = instance_form.build_form()
        self.page.update()

