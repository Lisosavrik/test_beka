import json

def get_file_json(file: str):
    with open(file, "r") as file_json:
        data = json.load(file_json)
        return data




