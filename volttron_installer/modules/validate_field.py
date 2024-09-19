from flet import TextField, IconButton, colors
import csv
import io
import json
import yaml

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

    submit_button.update()
    text_field.update()

def check_json_field(field: TextField) -> bool:
    """
    Validates the JSON input in a text field.
    Args:
        field (TextField): The text field containing JSON input.
    """
    custom_json = field.value.strip()  # Stripping whitespace

    if not custom_json:
        field.border_color = "black"
        field.update()
        return False

    try:
        loaded_json = json.loads(custom_json)
        field.border_color = colors.GREEN
        field.color = "white"
        field.value = json.dumps(loaded_json, indent=4)
        field.update()
        return True
    except json.JSONDecodeError:
        field.border_color = colors.RED_800
        field.color = colors.RED_800
        field.update()
        return False

def check_csv_field(field: TextField) -> bool:
    """
    Validates the CSV input in a text field.
    Args:
        field (TextField): The text field containing CSV input.
    """
    custom_csv = field.value.strip()  # Stripping whitespace

    if not custom_csv:
        field.border_color = "black"
        field.update()
        return True

    try:
        vcsv_file = io.StringIO(custom_csv)
        reader = csv.reader(vcsv_file)
        
        # Attempt to read the file to confirm it's valid
        for row in reader:
            pass

        field.border_color = colors.GREEN
        field.color = "white"
        field.update()
        return True
    except Exception as e:
        print(f"check_csv_field has error validating CSV: {e}")
        field.border_color = colors.RED_800
        field.color = colors.RED_800
        field.update()
        return False
    
def check_yaml_field(yaml_string) -> None:
    try:
        yaml.safe_load(yaml_string)
        print("calm yaml")
        return True
    except yaml.YAMLError:
        print("HE LYIN")
        return False