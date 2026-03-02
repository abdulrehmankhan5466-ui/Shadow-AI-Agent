# Reset-And-Setup-Shadow.ps1
# Moves old files to Unused folder + creates fresh working files

Write-Host "Shadow AI - Reset and Setup Script" -ForegroundColor Cyan
Write-Host "This will move old files to 'Unused' folder and create new clean ones." -ForegroundColor Yellow
Write-Host "Press Ctrl+C to cancel, or Enter to continue..." -ForegroundColor Yellow
Read-Host

$Root = "D:\Shadow-AI-Companion"
$Scripts = "$Root\scripts"
$Unused = "$Scripts\Unused"

# Create Unused folder if missing
if (-not (Test-Path $Unused)) {
    New-Item -Path $Unused -ItemType Directory | Out-Null
    Write-Host "Created backup folder: $Unused" -ForegroundColor Green
}

# Move old files to Unused (if they exist)
$oldFiles = @("ui.py", "main.py", "app.py", "chat.py", "input.py", "sidebar.py", "memory.py", "llm.py", "helpers.py")
foreach ($file in $oldFiles) {
    $path = "$Scripts\$file"
    if (Test-Path $path) {
        Move-Item -Path $path -Destination $Unused -Force
        Write-Host "Moved old file to Unused: $file" -ForegroundColor Yellow
    }
}

# Create fresh files with latest working code

# 1. main.py
$main = @'
from app import ShadowProfessionalUI

if __name__ == "__main__":
    app = ShadowProfessionalUI()
    app.mainloop()
'@
Set-Content -Path "$Scripts\main.py" -Value $main -Encoding UTF8

# 2. app.py
$app = @'
import customtkinter as ctk
from tkinter import END
from sidebar import create_sidebar
from input import create_input_area
from chat import create_chat_area, add_message, clear_chat
from memory import load_profile
from helpers import load_image

class ShadowProfessionalUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Shadow – Abdulrehman's AI Companion")
        self.geometry("1150x780")
        self.minsize(900, 600)

        self.profile = load_profile()

        self.shadow_avatar = load_image("avatar_shadow.png")
        self.user_avatar   = load_image("avatar_user.png")
        self.send_icon     = load_image("send_icon.png", (120, 60))

        self.sidebar = create_sidebar(self)
        self.chat_frame = create_chat_area(self)
        self.input_frame = create_input_area(self, self.send_message, self.handle_enter, self.send_icon)

        add_message(self, "Shadow", f"Hello Abdulrehman! I'm ready 😊 What’s on your mind?")

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def send_message(self):
        text = self.input_box.get("0.0", END).strip()
        if not text:
            return
        add_message(self, "Abdulrehman", text)
        self.input_box.delete("0.0", END)

        # Fake reply (replace with LLM later)
        add_message(self, "Shadow", f"Received: {text}")

    def handle_enter(self, event):
        if not event.state & 0x0001:
            self.send_message()
            return "break"

    def clear_chat(self):
        clear_chat(self)

    def show_known_facts(self):
        facts = "\n".join(f"- {f}" for f in self.profile["other_facts"]) if self.profile["other_facts"] else "Nothing special yet — tell me more!"
        add_message(self, "Shadow", f"What I know about you so far:\n\n{facts}")

    def open_settings(self):
        win = ctk.CTkToplevel(self)
        win.title("Settings")
        win.geometry("500x400")
        ctk.CTkLabel(win, text="Settings (coming soon)", font=("Segoe UI", 18)).pack(pady=140)

    def on_closing(self):
        self.destroy()
'@
Set-Content -Path "$Scripts\app.py" -Value $app -Encoding UTF8

# 3. sidebar.py
$sidebar = @'
import customtkinter as ctk

def create_sidebar(parent):
    sidebar = ctk.CTkFrame(parent, width=260, corner_radius=0, fg_color="#0a0a0a")
    sidebar.pack(side="left", fill="y")

    ctk.CTkLabel(sidebar, text="Shadow", font=("Segoe UI", 28, "bold")).pack(pady=(60, 10))
    ctk.CTkLabel(sidebar, text="Abdulrehman's AI", font=("Segoe UI", 13), text_color="#64748b").pack()

    ctk.CTkButton(sidebar, text="Clear Chat", height=42, corner_radius=12,
                  command=parent.clear_chat).pack(pady=(50, 10), padx=24, fill="x")

    ctk.CTkButton(sidebar, text="What do you know about me?", height=42, corner_radius=12,
                  fg_color="#7c3aed", hover_color="#9333ea",
                  command=parent.show_known_facts).pack(pady=10, padx=24, fill="x")

    ctk.CTkButton(sidebar, text="Settings", height=42, corner_radius=12,
                  command=parent.open_settings).pack(pady=10, padx=24, fill="x")

    return sidebar
'@
Set-Content -Path "$Scripts\sidebar.py" -Value $sidebar -Encoding UTF8

# 4. chat.py
$chat = @'
import customtkinter as ctk
from datetime import datetime

def create_chat_area(parent):
    chat_frame = ctk.CTkScrollableFrame(parent, fg_color="#0d0d0d")
    chat_frame.pack(padx=30, pady=(20, 10), fill="both", expand=True)
    parent.chat_frame = chat_frame
    return chat_frame

def add_message(parent, sender, text):
    is_shadow = sender == "Shadow"
    bubble_color = "#1e2937" if is_shadow else "#166534"
    align = "w" if is_shadow else "e"

    container = ctk.CTkFrame(parent.chat_frame, fg_color="transparent")
    container.pack(anchor=align, padx=28, pady=6, fill="x")

    bubble = ctk.CTkFrame(container, fg_color=bubble_color, corner_radius=22)
    bubble.pack(anchor=align)

    row = ctk.CTkFrame(bubble, fg_color="transparent")
    row.pack(padx=16, pady=12, fill="x")

    av = parent.shadow_avatar if is_shadow else parent.user_avatar
    if av:
        ctk.CTkLabel(row, image=av, text="").pack(side="left" if is_shadow else "right", padx=(0, 12) if is_shadow else (12, 0))

    msg_label = ctk.CTkLabel(row, text=text, font=("Segoe UI", 14), wraplength=600, justify="left", text_color="#e2e8f0", anchor="w")
    msg_label.pack(side="left", fill="x", expand=True)

    def copy_action(t=text):
        parent.clipboard_clear()
        parent.clipboard_append(t)
        temp = ctk.CTkLabel(parent, text="Copied!", text_color="#22c55e", fg_color="#0d0d0d")
        temp.place(relx=0.5, rely=0.95, anchor="center")
        parent.after(1800, temp.destroy)

    copy_btn = ctk.CTkButton(row, text="📋", width=30, height=30, corner_radius=8, fg_color="transparent", hover_color="#334155", text_color="#94a3b8", command=copy_action)
    copy_btn.pack(side="right", padx=8)

    time_str = (Get-Date).ToString("hh:mm tt")
    ctk.CTkLabel(bubble, text=time_str, font=("Segoe UI", 10), text_color="#ffffff").pack(anchor="e", padx=16, pady=(0, 8))

    parent.chat_frame.after(80, { $parent.chat_frame._parent_canvas.yview_moveto(1.0) })
'@

Set-Content -Path "$Scripts\chat.py" -Value $chat -Encoding UTF8

# 5. input.py
$input = @'
import customtkinter as ctk

def create_input_area(parent, send_callback, enter_callback, send_icon):
    input_frame = ctk.CTkFrame(parent, fg_color="#0d0d0d", height=70)
    input_frame.pack(padx=30, pady=(0, 24), fill="x")

    parent.input_box = ctk.CTkTextbox(input_frame, height=52, font=("Segoe UI", 14.5), corner_radius=16)
    parent.input_box.pack(side="left", fill="x", expand=True, padx=(0, 12))
    parent.input_box.bind("<Return>", enter_callback)

    send_btn = ctk.CTkButton(input_frame, text="", image=send_icon,
                             width=120, height=60, corner_radius=16,
                             fg_color="#238636", hover_color="#2ea043",
                             command=send_callback)
    send_btn.pack(side="right")

    return input_frame
'@

Set-Content -Path "$Scripts\input.py" -Value $input -Encoding UTF8

Write-Host ""
Write-Host "All files reset and created successfully!" -ForegroundColor Green
Write-Host "Old files moved to: $Unused"
Write-Host ""
Write-Host "To run the app:"
Write-Host "   python scripts\main.py"
Write-Host ""
Write-Host "Press Enter to exit..."
Read-Host