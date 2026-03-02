import json
import os

DATA_DIR = r"D:\Shadow-AI-Companion\data"
PROFILE_FILE = os.path.join(DATA_DIR, 'user_profile.json')

DEFAULT_PROFILE = {
    "full_name": "Abdulrehman Khan",
    "first_name": "Abdulrehman",
    "age": "24",
    "job": "3D artist and Graphic designer",
    "location": "Lahore Pakistan",
    "tools": ["Blender"],
    "other_facts": ["I don't like cricket"],
    "theme": "dark-blue"
}

def load_profile():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    profile = DEFAULT_PROFILE.copy()
    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                profile.update(json.load(f))
        except:
            pass
    return profile

def save_profile(profile):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(PROFILE_FILE, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)

def learn_new_fact(profile, new_fact):
    if new_fact not in profile["other_facts"]:
        profile["other_facts"].append(new_fact)
        save_profile(profile)
        return True
    return False