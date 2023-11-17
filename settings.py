import json

def load_settings():
    with open('config/settings.json') as settings_file:
        return json.load(settings_file)
