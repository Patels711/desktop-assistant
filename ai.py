import json
from datetime import datetime, timedelta

from ollama import chat

from notes import (
    create_note,
    show_notes,
    find_notes,
    get_note_body,
    append_note,
    delete_note,
    open_note
)

from presets import (
    get_time,
    open_application,
    quit_application,
    close_window_application,
    APPLICATIONS,
    show_desktop,
    hide_desktop
)

MODEL = "qwen3:8b"

SYSTEM_PROMPT = """
You are the AI brain of a Mac desktop assistant called Jarvis.

Understand the user's request naturally. Do not require exact command phrases.

Use tools whenever the user asks you to perform an action on the Mac.
Do not claim an action was completed unless the tool result confirms it.

For normal conversation, answer naturally without using a tool.

Notes:
- "my Gatsby note" means the note named "Gatsby".
- If the user does not specify a note folder, use "all".
- "AP notes" means folder "APs".
- "college notes" means folder "college".
- "ECS notes" means folder "ECS".
- "important study notes" means folder "Imp Study Notes" when clearly referring to that folder.
- "quick notes" means folder "Quick Notes".
- "schedule" means folder "SCHEDULE".
- "everything", "all my notes", or "all notes" means folder "all".
- Never invent a note name or folder.
- Preserve note names and note content exactly as provided by the user.
- "none" or "default" means the default Notes folder.

Applications:
- Use the application tools for opening, quitting, or closing applications.
- The application tool accepts common aliases such as chrome, browser, vscode, code, notes, spotify, messages, calendar, finder, safari, terminal, todoist, and arc.
- Do not invent an application name.

Dates:
- Use the date tool for date requests.
- Today is offset 0, tomorrow is 1, yesterday is -1.
- Calculate other relative dates using the appropriate integer offset.
- Do not calculate or state the current date yourself when a date tool is available.

Time:
- Use the time tool for requests about the current time.

Desktop:
- Use the desktop tools when the user asks to show or hide desktop icons.

When a tool reports an error, explain the actual result instead of pretending it worked.

Keep responses concise unless the user asks for more detail.
"""


def create_note_tool(name: str, body: str, folder: str = "default") -> str:
    if folder.lower() in {"default", "none"}:
        folder = None

    result = create_note(name, body, folder)

    if result == "folder_not_found":
        return f"I couldn't find a folder called '{folder}'."

    if result == "deleted_folder":
        return "I can't create notes in Recently Deleted."

    if result.startswith("success"):
        parts = result.split("||", 1)

        if len(parts) == 2 and parts[1]:
            return f"Created '{name}' in the '{parts[1]}' folder."

        return f"Created '{name}'."

    return f"I couldn't create '{name}'."


def show_notes_tool(folder: str = "all") -> str:
    notes = show_notes(folder)

    if not notes:
        return f"I couldn't find any notes in '{folder}'."

    return json.dumps(
        notes,
        ensure_ascii=False
    )


def find_note_tool(name: str, folder: str = "all") -> str:
    matches = find_notes(name, folder)

    if not matches:
        return f"I couldn't find a note called '{name}'."

    results = []

    for note in matches:
        item = dict(note)

        if not note["deleted"]:
            item["body"] = get_note_body(
                note["name"],
                note["folder"]
            )

        results.append(item)

    return json.dumps(
        results,
        ensure_ascii=False
    )


def append_note_tool(
    name: str,
    text: str,
    folder: str = "all"
) -> str:

    matches = find_notes(name, folder)

    if not matches:
        return f"I couldn't find a note called '{name}'."

    active_matches = [
        note for note in matches
        if not note["deleted"]
    ]

    if not active_matches:
        return "I can't modify notes in Recently Deleted."

    if len(active_matches) > 1:
        return json.dumps(
            {
                "status": "multiple",
                "matches": [
                    {
                        "name": note["name"],
                        "folder": note["folder"],
                        "account": note["account"]
                    }
                    for note in active_matches
                ]
            },
            ensure_ascii=False
        )

    note = active_matches[0]

    result = append_note(
        note["name"],
        note["folder"],
        text
    )

    if result == "success":
        return f"Added to '{note['name']}'."

    if result == "deleted":
        return "I can't modify notes in Recently Deleted."

    return f"I couldn't modify '{note['name']}'."


def delete_note_tool(
    name: str,
    folder: str = "all"
) -> str:

    matches = find_notes(name, folder)

    if not matches:
        return f"I couldn't find a note called '{name}'."

    active_matches = [
        note for note in matches
        if not note["deleted"]
    ]

    if not active_matches:
        return "I can't modify notes in Recently Deleted."

    if len(active_matches) > 1:
        return json.dumps(
            {
                "status": "multiple",
                "matches": [
                    {
                        "name": note["name"],
                        "folder": note["folder"],
                        "account": note["account"]
                    }
                    for note in active_matches
                ]
            },
            ensure_ascii=False
        )

    note = active_matches[0]

    result = delete_note(
        note["name"],
        note["folder"]
    )

    if result == "success":
        return f"Deleted '{note['name']}'."

    if result == "deleted":
        return "I can't modify notes in Recently Deleted."

    return f"I couldn't delete '{note['name']}'."


def open_note_tool(
    name: str,
    folder: str = "all"
) -> str:

    matches = find_notes(name, folder)

    if not matches:
        return f"I couldn't find a note called '{name}'."

    active_matches = [
        note for note in matches
        if not note["deleted"]
    ]

    if not active_matches:
        return "I can't open notes in Recently Deleted."

    if len(active_matches) > 1:
        return json.dumps(
            {
                "status": "multiple",
                "matches": [
                    {
                        "name": note["name"],
                        "folder": note["folder"],
                        "account": note["account"]
                    }
                    for note in active_matches
                ]
            },
            ensure_ascii=False
        )

    note = active_matches[0]

    result = open_note(
        note["name"],
        note["folder"]
    )

    if result == "success":
        return f"Opened '{note['name']}'."

    if result == "deleted":
        return "I can't open notes in Recently Deleted."

    return f"I couldn't open '{note['name']}'."


def date_tool(offset: int = 0) -> str:
    try:
        offset = int(offset)
    except (TypeError, ValueError):
        offset = 0

    date = datetime.now() + timedelta(days=offset)

    if offset == 0:
        return f"Today is {date.strftime('%A, %B %-d, %Y')}."

    if offset == 1:
        return f"Tomorrow is {date.strftime('%A, %B %-d, %Y')}."

    if offset == -1:
        return f"Yesterday was {date.strftime('%A, %B %-d, %Y')}."

    return date.strftime(
        "%A, %B %-d, %Y."
    )


def time_tool() -> str:
    return f"The current time is {get_time()}."


def resolve_application(application: str):
    key = application.strip().lower()
    return APPLICATIONS.get(key)


def open_application_tool(application: str) -> str:
    resolved = resolve_application(application)

    if not resolved:
        return f"I don't know the application '{application}'."

    open_application(resolved)

    return f"Opening {resolved}."


def quit_application_tool(application: str) -> str:
    resolved = resolve_application(application)

    if not resolved:
        return f"I don't know the application '{application}'."

    quit_application(resolved)

    return f"Quitting {resolved}."


def close_application_tool(application: str) -> str:
    resolved = resolve_application(application)

    if not resolved:
        return f"I don't know the application '{application}'."

    close_window_application(resolved)

    return f"Closing the current window of {resolved}."


def show_desktop_tool() -> str:
    return show_desktop()


def hide_desktop_tool() -> str:
    return hide_desktop()


TOOLS = [
    create_note_tool,
    show_notes_tool,
    find_note_tool,
    append_note_tool,
    delete_note_tool,
    open_note_tool,
    date_tool,
    time_tool,
    open_application_tool,
    quit_application_tool,
    close_application_tool,
    show_desktop_tool,
    hide_desktop_tool
]


TOOL_MAP = {
    tool.__name__: tool
    for tool in TOOLS
}


messages = [
    {
        "role": "system",
        "content": SYSTEM_PROMPT
    }
]


def ask_ai(user_input):
    messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    for _ in range(5):
        response = chat(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            think=False
        )

        messages.append(response.message)

        if not response.message.tool_calls:
            return response.message.content.strip()

        for call in response.message.tool_calls:
            tool_name = call.function.name
            tool = TOOL_MAP.get(tool_name)

            if not tool:
                result = f"Unknown tool: {tool_name}"
            else:
                try:
                    result = tool(
                        **call.function.arguments
                    )
                except Exception as e:
                    result = f"Tool error: {e}"

            messages.append(
                {
                    "role": "tool",
                    "tool_name": tool_name,
                    "content": str(result)
                }
            )

    return "I couldn't complete that request."


def process(user_input):
    try:
        return ask_ai(user_input)
    except Exception as e:
        return f"AI error: {e}"


def main():
    print("Jarvis AI ready.")
    print("Type 'exit' to quit.")
    print()

    while True:
        try:
            user_input = input("> ").strip()

        except (EOFError, KeyboardInterrupt):
            break

        if not user_input:
            continue

        if user_input.lower() == "exit":
            break

        result = process(user_input)

        print(f"Assistant: {result}")
        print()


if __name__ == "__main__":
    main()