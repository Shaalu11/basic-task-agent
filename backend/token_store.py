import os
import json

TOKEN_DIR = "tokens"

if not os.path.exists(TOKEN_DIR):
    os.makedirs(TOKEN_DIR)

def save_token(email, token):
    with open(f"{TOKEN_DIR}/{email}.json", "w") as f:
        json.dump(token, f)

def load_token(email):
    path = f"{TOKEN_DIR}/{email}.json"
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return None

def delete_token(email):
    path = f"{TOKEN_DIR}/{email}.json"
    if os.path.exists(path):
        os.remove(path)
        return True
    return False