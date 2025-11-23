import json, os, hashlib

USERS_FILE = "users.json"

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(data):
    with open(USERS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

# session state for login
if "quiz_user" not in st.session_state:
    st.session_state.quiz_user = None
