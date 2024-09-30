import json
import os
from werkzeug.security import generate_password_hash, check_password_hash

class UserManager:
    def __init__(self, auth_file='auth.json'):
        self.auth_file = auth_file
        self.data = {
            "users": {},
            "api_keys": {}
        }
        if os.path.exists(self.auth_file):
            with open(self.auth_file, 'r') as f:
                self.data = json.load(f)
        else:
            self.save_data()

    def save_data(self):
        with open(self.auth_file, 'w') as f:
            json.dump(self.data, f, indent=4)

    def add_user(self, username, password, usertype=1):
        self.data['users'][username] = {
            'password': password,
            'usertype': usertype
        }
        self.save_data()

    def remove_user(self, username):
        if username in self.data['users']:
            del self.data['users'][username]
            # Also remove API keys associated with this user
            self.data['api_keys'] = {k: v for k, v in self.data['api_keys'].items() if v != username}
            self.save_data()

    def authenticate_user(self, username, password):
        user = self.data['users'].get(username)
        if user and user['usertype'] > 0:
            return user['password'] == password
        return False

    def get_user(self, username):
        return self.data['users'].get(username)

    def list_users(self):
        return self.data['users']

    def add_api_key(self, username, api_key):
        self.data['api_keys'][api_key] = username
        self.save_data()

    def remove_api_key(self, api_key):
        if api_key in self.data['api_keys']:
            del self.data['api_keys'][api_key]
            self.save_data()

    def get_username_for_api_key(self, api_key):
        return self.data['api_keys'].get(api_key)

    def list_api_keys_for_user(self, username):
        return [k for k, v in self.data['api_keys'].items() if v == username]
