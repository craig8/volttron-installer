from volttron_installer.modules.prettify_string import prettify_json, prettify_yaml
from flet import *

class ConfigFilePicker(Control):
    """File picker control to handle the uploads of yaml, csv, and 
    json config files"""
    def __init__(self, page: Page):
        self.page = page
        self.file_picker = FilePicker(on_result=self.route_correct_method)
        self.page.overlay.append(self.file_picker)
        self.extension_methods: dict[callable] = { 
            "csv": self.csv_picker_method,
            "json": self.json_picker_method,
            "yaml": self.yaml_picker_method
        }

    def route_correct_method(self, e: FilePickerResultEvent) -> None:
        if e.files:

            print("\nThis is the e.files:", e.files)
            print("\nThis is the file we picked:", e.files[0])

            # we can only pick one file at a time anyway,
            # so we can just grab the first file we see in the e.files list
            picked_file = e.files[0]

            # Grab the extension of the file:
            extension = picked_file.name.split('.')[-1]

            # According to file extension, grab the correct method
            # and use it
            correct_method = self.extension_methods[extension]
            correct_method(picked_file.path)
        return

    def csv_picker_method(self, data: str) -> str: 
        # self.file_picker.on_whatever = 
        return

    def yaml_picker_method(self, data: str) -> str: 
        return
    
    def json_picker_method(self, data: str) -> str: 
        return
    
    def launch_file_picker(self, allowed_extensions: list[str]):
        self.file_picker.pick_files(allowed_extensions=allowed_extensions)
