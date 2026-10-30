import subprocess
from datetime import datetime
import os


#basic functions
def open_application(application):
    subprocess.Popen(["open", "-a", application])

def quit_application (application):
    subprocess.run(["osascript", "-e", f'tell application "{application}" to quit'])

def close_window_application (application):
    subprocess.run(["osascript", "-e", f'tell application "{application}" to close front window'])

def get_time():
    return datetime.now().strftime("%I:%M %p")

def get_date():
    return datetime.now().strftime("%B %d, %Y")

def command_terminal(command):
    subprocess.run([f"{command}"])

#functions carried out
def open_browser():
    open_application("Google Chrome")
    return "Opening Google Chrome."


def open_terminal():
    open_application("Terminal")
    return "Opening Terminal."


def open_vscode():
    open_application("Visual Studio Code")
    return "Opening Visual Studio Code."


def quit_browser():
    quit_application("Google Chrome")
    return "Quitting Google Chrome."

def quit_terminal():
    quit_application("Terminal")
    return "Quitting Terminal."

def quit_vscode():
    quit_application("Visual Studio Code")
    return "Quitting Visual Studio Code."

def close_browser():
    close_window_application("Google Chrome")
    return "Closing Google Chrome window."

def close_terminal():
    close_window_application("Terminal")
    return "Closing Terminal." 

def close_vscode():
    close_window_application("Visual Studio Code")
    return "Closing Visual Studio Code."

def show_desktop():
    subprocess.run([
        "open",
        "-a",
        os.path.expanduser("~/Documents/Show Desktop.app")
    ])
    return "Desktop icons shown."

def hide_desktop():
    subprocess.run([
        "open",
        "-a",
        os.path.expanduser("~/Documents/Hide Desktop.app")
    ])
    return "Desktop icons hidden."

#preset dictionary
PRESETS = {
    "open browser": open_browser,
    "open terminal": open_terminal,
    "open vscode": open_vscode,

    "quit browser": quit_browser,
    "quit vscode": quit_vscode,
    "quit terminal": quit_terminal,

    "close browser": close_browser,
    "close terminal": close_terminal,
    "close vscode": close_vscode,
    "show desktop":show_desktop,
    "hide desktop":hide_desktop,
}

APPLICATIONS = {
    "chrome": "Google Chrome",
    "browser": "Google Chrome",
    "google chrome": "Google Chrome",
    "arc": "Arc",
    "todoist": "Todoist",
    "todo": "Todoist",
    "siri": "Siri",
    "telegram": "Telegram",
    "preview": "Preview",

    "terminal": "Terminal",

    "vscode": "Visual Studio Code",
    "visual studio code": "Visual Studio Code",
    "code": "Visual Studio Code",

    "safari": "Safari",
    "finder": "Finder",
    "notes": "Notes",
    "messages": "Messages",
    "calendar": "Calendar",
}