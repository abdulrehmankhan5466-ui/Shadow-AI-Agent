from customtkinter import CTkImage
from PIL import Image
import os

ASSETS_DIR = r"D:\Shadow-AI-Companion\scripts\assets"

def load_image(name, size=(42, 42)):
    path = os.path.join(ASSETS_DIR, name)
    if not os.path.exists(path):
        return None
    try:
        img = Image.open(path).resize(size, Image.Resampling.LANCZOS)
        return CTkImage(light_image=img, dark_image=img, size=size)
    except:
        return None