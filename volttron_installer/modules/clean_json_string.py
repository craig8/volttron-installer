import json

def clean_json_string(json_string: str) -> dict:
    if isinstance(json_string, str) == False:
        return json_string #
    parced_string = json_string.replace("\r", "").replace("\\", "").replace("\n" , "").replace(" ", "")
    try:
        decoded_string = json.loads(parced_string)
        cleaned_string = json.dumps(decoded_string)
        return cleaned_string
    except:
        return parced_string