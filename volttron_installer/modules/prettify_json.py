import json

def prettify_json(string: str) -> str:
    if not string:  # This correctly checks if the string is empty or None
        return string
    try:
        parsed_json_data = json.loads(string)
        pretty_json_data = json.dumps(parsed_json_data, indent=4)
        return pretty_json_data
    except json.JSONDecodeError:
        print("Error occurred parsing supposed JSON string:", string)
        return string