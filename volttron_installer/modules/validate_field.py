from flet import TextField, IconButton, colors
import csv
import io
import json
import yaml
import re
from volttron_installer.modules.attempt_to_update_control import attempt_to_update_control

def validate_text(text_field: TextField, submit_button: IconButton) -> None:
    """
    Validates the text in `text_field` and updates the `submit_button` accordingly.
    Args:
        text_field (TextField): The text field to validate.
        submit_button (IconButton): The submit button to enable/disable based on validation.
    """
    valid_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
    input_text = text_field.value.strip()  # Stripping whitespace

    if all(c in valid_chars for c in input_text):
        text_field.error_text = None
        submit_button.disabled = False
    else:
        text_field.error_text = "Only letters, numbers, and underscores are allowed."
        submit_button.disabled = True

    attempt_to_update_control(submit_button)
    attempt_to_update_control(text_field)

def check_json_field(field: TextField | str) -> bool:

    if isinstance(field, TextField):
        custom_json = field.value.strip()  # Stripping whitespace
    else:
        custom_json = field.strip()

    custom_json: str = field.value.strip()
    custom_json = re.sub(r"'", '"', custom_json)

    if not custom_json:
        field.border_color = "black"
        field.update()
        return False

    try:
        loaded_json = json.loads(custom_json)
        field.border_color = "green"
        field.color = "white"
        field.value = json.dumps(loaded_json, indent=4)
        field.update()
        return True
    except json.JSONDecodeError:
        field.border_color = "red"
        field.color = "red"
        field.update()
        return False

def check_csv_field(field: TextField | str) -> bool:
    """
    Validates the CSV input in a text field.
    Args:
        field (TextField): The text field containing CSV input.
    """
    if isinstance(field, TextField):
        custom_csv = field.value.strip()  # Stripping whitespace
    else:
        custom_csv = field.strip()

    if not custom_csv:
        field.border_color = "black"
        attempt_to_update_control(field)
        return True

    try:
        vcsv_file = io.StringIO(custom_csv)
        reader = csv.reader(vcsv_file)
        
        # Attempt to read the file to confirm it's valid
        for row in reader:
            pass

        field.border_color = colors.GREEN
        field.color = "white"
        attempt_to_update_control(field)
        return True
    except Exception as e:
        # print(f"check_csv_field has error validating CSV: {e}")
        field.border_color = colors.RED_800
        field.color = colors.RED_800
        attempt_to_update_control(field)
        return False
    
def check_yaml_field(yaml_field: TextField | str) -> bool:
    if isinstance(yaml_field, TextField):
        yaml_string = yaml_field.value.strip()  # Stripping whitespace
    else:
        yaml_string = yaml_field.strip()

    try:
        yaml.safe_load(yaml_string)
        yaml_field.border_color = "green"
        yaml_field.color = "white"
        yaml_field.update()
        return True
    except yaml.YAMLError:
        return False

def replace_single_quotes(data: str) -> str:
    # Replace single quotes with double quotes
    return data.replace("'", '"')

def check_format(data: str) -> str:
    data = replace_single_quotes(data)  # Normalize the quotes

    try:
        json.loads(data)
        return "JSON"
    except json.JSONDecodeError:
        # It didn't work as JSON, continue to YAML check
        pass
    
    try:
        yaml.safe_load(data)
        return "YAML"
    except yaml.YAMLError:
        pass

    return "UNKNOWN"
