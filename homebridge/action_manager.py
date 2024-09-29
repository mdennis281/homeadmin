import json

class ActionManager:
    def __init__(self, actions_file='saved-actions.json'):
        self.actions_file = actions_file

    def list(self):
        """Reads the JSON file and returns it as a dictionary."""
        try:
            with open(self.actions_file, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def save(self, action_name: str, action: dict):
        """Writes a new action to the JSON file."""
        data = self.list()  # Load existing data
        data[action_name] = action
        with open(self.actions_file, 'w') as file:
            json.dump(data, file, indent=2)

    def get(self, action_name: str) -> dict:
        """Returns a specific action from the JSON file."""
        data = self.list()
        return data.get(action_name, None)