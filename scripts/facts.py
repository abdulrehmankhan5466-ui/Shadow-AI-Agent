import json
import os

DATA_DIR = r"D:\Shadow-AI-Companion0\Repositries\Shadow-AI-Agent\data"
PROFILE_FILE = os.path.join(DATA_DIR, 'user_profile.json')

DEFAULT_PROFILE = {
    "full_name": "Abdulrehman Khan",
    "first_name": "Abdulrehman",
    "age": "24",
    "job": "3D artist and Graphic designer",
    "location": "Lahore Pakistan",
    "tools": ["Blender", "Photoshop", "After Effects"],  # added common ones — edit as you like
    "other_facts": [
        "I don't like cricket",
        "I prefer dark mode in everything",
        "Love chai more than coffee"
    ],
    "theme": "dark-blue"
}


def load_profile():
    os.makedirs(DATA_DIR, exist_ok=True)
    profile = DEFAULT_PROFILE.copy()
    
    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                profile.update(loaded)
        except Exception as e:
            print(f"Profile load error: {e} — using defaults")
    
    return profile


def save_profile(profile):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(PROFILE_FILE, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)


def learn_new_fact(profile, new_fact: str):
    """Returns True if fact was new and saved"""
    cleaned = new_fact.strip()
    if not cleaned:
        return False
    
    if cleaned not in profile["other_facts"]:
        profile["other_facts"].append(cleaned)
        save_profile(profile)
        return True
    return False