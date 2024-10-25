import json

def clean_json_string(json_string: str) -> dict:
    if isinstance(json_string, str) == False:
        return json_string # if not a string, return
    # print("parcing time baby")
    parced_string = json_string.replace("\r", "").replace("\\", "").replace("\n" , "").replace(" ", "")
    try:
        return json.loads(parced_string)
    except json.JSONDecodeError:
        return parced_string