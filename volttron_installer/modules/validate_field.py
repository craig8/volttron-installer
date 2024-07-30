from flet import TextField, IconButton

def validate_text(text_field: TextField, submit_button: IconButton) -> None:
    """
    Validates the text in `text_field` and updates the `submit_button` accordingly.

    Args:
        text_field (TextField): The text field to validate.
        submit_button (IconButton): The submit button to enable/disable based on validation.
    """
    valid_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
    input_text = text_field.value
    if all(c in valid_chars for c in input_text):
        text_field.error_text = None
        submit_button.disabled = False
    else:
        text_field.error_text = "Only letters, numbers, and underscores are allowed."
        submit_button.disabled = True

    submit_button.update()
    text_field.update()