import json

# Load the list of dictionaries from the JSON file
def load_from_file(filename='cars_data.json'):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []  # Return an empty list if the file doesn't exist


# Load the list of dictionaries from the file
cars = load_from_file()