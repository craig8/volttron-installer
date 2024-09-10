import json

def prettify_json(string: str) -> str:
    if string == "" or None:
        return string
    else:
        try:
            parsed_json_data = json.loads(string)
            pretty_json_data = json.dumps(parsed_json_data, indent=4)
            return pretty_json_data
        except:
            #print("Error occurred parsing supposed JSON string:", string)
            return string