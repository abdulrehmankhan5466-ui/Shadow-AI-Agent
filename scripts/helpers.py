from customtkinter import CTkImage   # ← actually not used in Streamlit version anymore
from PIL import Image
import os

ASSETS_DIR = r"D:\Shadow-AI-Companion\scripts\assets"


def load_image(name, size=(42, 42)):
    """Used in old CustomTkinter version — keeping for future reference"""
    path = os.path.join(ASSETS_DIR, name)
    if not os.path.exists(path):
        return None
    try:
        img = Image.open(path).resize(size, Image.Resampling.LANCZOS)
        return CTkImage(light_image=img, dark_image=img, size=size)
    except Exception:
        return None


def get_asset_path(filename):
    """Helper for Streamlit — returns full path to asset"""
    return os.path.join(ASSETS_DIR, filename)