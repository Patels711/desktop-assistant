import subprocess



DELETED_FOLDERS = {
    "recently deleted",
    "deleted",
    "trash",
    "bin"
}

ALL_FOLDER_ALIASES = {
    "all",
    "all icloud",
    "everywhere",
    "all notes"
}

DEFAULT_FOLDER_ALIASES = {
    "none",
    "default"
}



def run_script(script):
    result = subprocess.run(
        ["osascript"],
        input=script,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"AppleScript error: {result.stderr.strip()}")
        return ""

    return result.stdout.strip()

def show_notes(folder="all"):
    return get_notes(folder)

def escape(text):
    return (
        str(text)
        .replace("\\", "\\\\")
        .replace('"', '\\"')
    )


def normalize(text):
    return str(text).strip().strip(" .!?").lower()


def is_deleted(folder):
    return normalize(folder) in DELETED_FOLDERS


def is_all_folder(folder):
    return normalize(folder or "all") in ALL_FOLDER_ALIASES


def is_default_folder(folder):
    return normalize(folder or "") in DEFAULT_FOLDER_ALIASES


def resolve_folder(folder):
    folder_name = normalize(folder)

    for item in get_folders():
        if normalize(item["folder"]) == folder_name:
            return item

    return None



def get_folders():
    script = '''
tell application "Notes"
    set output to ""

    set accountList to accounts

    repeat with accountRef in accountList
        set currentAccount to contents of accountRef
        set folderList to folders of currentAccount

        repeat with folderRef in folderList
            set currentFolder to contents of folderRef

            set output to output & ¬
                (name of currentAccount) & "||" & ¬
                (name of currentFolder) & linefeed
        end repeat
    end repeat

    return output
end tell
'''

    result = run_script(script)

    folders = []

    for line in result.splitlines():
        parts = line.split("||", 1)

        if len(parts) == 2:
            folders.append({
                "account": parts[0],
                "folder": parts[1],
                "deleted": is_deleted(parts[1])
            })

    return folders



def get_notes(folder="all"):
    folder = (folder or "all").strip()

    search_all = is_all_folder(folder)

    script = '''
tell application "Notes"
    set output to ""

    set accountList to accounts

    repeat with accountRef in accountList
        set currentAccount to contents of accountRef
        set folderList to folders of currentAccount

        repeat with folderRef in folderList
            set currentFolder to contents of folderRef

            set noteList to notes of currentFolder

            repeat with noteRef in noteList
                set currentNote to contents of noteRef

                set output to output & ¬
                    (name of currentNote) & "||" & ¬
                    (name of currentFolder) & "||" & ¬
                    (name of currentAccount) & linefeed
            end repeat

        end repeat
    end repeat

    return output
end tell
'''

    result = run_script(script)

    notes = []

    for line in result.splitlines():
        parts = line.split("||")

        if len(parts) == 3:
            notes.append({
                "name": parts[0],
                "folder": parts[1],
                "account": parts[2],
                "deleted": is_deleted(parts[1])
            })

    if not search_all:
        notes = [
            note for note in notes
            if normalize(note["folder"]) == normalize(folder)
        ]

    return notes



def find_notes(name, folder="all"):
    name = normalize(name)

    notes = get_notes(folder)

    return [
        note
        for note in notes
        if normalize(note["name"]) == name
    ]



def get_note_body(name, folder):
    name = escape(name)
    folder = escape(folder)

    script = f'''
tell application "Notes"
    set accountList to accounts

    repeat with accountRef in accountList
        set currentAccount to contents of accountRef
        set folderList to folders of currentAccount

        repeat with folderRef in folderList
            set currentFolder to contents of folderRef

            if (name of currentFolder) is "{folder}" then

                set noteList to notes of currentFolder

                repeat with noteRef in noteList
                    set currentNote to contents of noteRef

                    if (name of currentNote) is "{name}" then
                        return body of currentNote
                    end if
                end repeat

            end if
        end repeat
    end repeat

    return ""
end tell
'''

    return run_script(script)



def create_note(name, body, folder=None):
    name = escape(name)
    body = escape(body)

    if folder and not is_default_folder(folder):

        resolved_folder = resolve_folder(folder)

        if not resolved_folder:
            return "folder_not_found"

        if resolved_folder["deleted"]:
            return "deleted_folder"

        folder = escape(resolved_folder["folder"])

        script = f'''
tell application "Notes"
    set accountList to accounts

    repeat with accountRef in accountList
        set currentAccount to contents of accountRef
        set folderList to folders of currentAccount

        repeat with folderRef in folderList
            set currentFolder to contents of folderRef

            if (name of currentFolder) is "{folder}" then
                make new note at currentFolder with properties {{name:"{name}", body:"{body}"}}

                return "success||" & (name of currentFolder)
            end if
        end repeat
    end repeat

    return "folder_not_found"
end tell
'''

    else:

        script = f'''
tell application "Notes"
    make new note with properties {{name:"{name}", body:"{body}"}}

    return "success"
end tell
'''

    return run_script(script)



def append_note(name, folder, text):
    matches = find_notes(name, folder)

    if not matches:
        return "not_found"

    active_matches = [
        note for note in matches
        if not note["deleted"]
    ]

    if not active_matches:
        return "deleted"

    if len(active_matches) > 1:
        return "multiple"

    note = active_matches[0]

    note_name = escape(note["name"])
    folder_name = escape(note["folder"])
    text = escape(text)

    script = f'''
tell application "Notes"
    set accountList to accounts

    repeat with accountRef in accountList
        set currentAccount to contents of accountRef
        set folderList to folders of currentAccount

        repeat with folderRef in folderList
            set currentFolder to contents of folderRef

            if (name of currentFolder) is "{folder_name}" then

                if (name of currentFolder) is "Recently Deleted" then
                    return "deleted"
                end if

                set noteList to notes of currentFolder

                repeat with noteRef in noteList
                    set currentNote to contents of noteRef

                    if (name of currentNote) is "{note_name}" then

                        set currentBody to body of currentNote

                        set body of currentNote to currentBody & "<br>{text}"

                        return "success"
                    end if
                end repeat

            end if
        end repeat
    end repeat

    return "not_found"
end tell
'''

    return run_script(script)



def delete_note(name, folder):
    matches = find_notes(name, folder)

    if not matches:
        return "not_found"

    active_matches = [
        note for note in matches
        if not note["deleted"]
    ]

    if not active_matches:
        return "deleted"

    if len(active_matches) > 1:
        return "multiple"

    note = active_matches[0]

    note_name = escape(note["name"])
    folder_name = escape(note["folder"])

    script = f'''
tell application "Notes"
    set accountList to accounts

    repeat with accountRef in accountList
        set currentAccount to contents of accountRef
        set folderList to folders of currentAccount

        repeat with folderRef in folderList
            set currentFolder to contents of folderRef

            if (name of currentFolder) is "{folder_name}" then

                if (name of currentFolder) is "Recently Deleted" then
                    return "deleted"
                end if

                set noteList to notes of currentFolder

                repeat with noteRef in noteList
                    set currentNote to contents of noteRef

                    if (name of currentNote) is "{note_name}" then
                        delete currentNote
                        return "success"
                    end if
                end repeat

            end if
        end repeat
    end repeat

    return "not_found"
end tell
'''

    return run_script(script)



def open_note(name, folder):
    matches = find_notes(name, folder)

    if not matches:
        return "not_found"

    active_matches = [
        note for note in matches
        if not note["deleted"]
    ]

    if not active_matches:
        return "deleted"

    if len(active_matches) > 1:
        return "multiple"

    note = active_matches[0]

    note_name = escape(note["name"])
    folder_name = escape(note["folder"])

    script = f'''
tell application "Notes"
    set accountList to accounts

    repeat with accountRef in accountList
        set currentAccount to contents of accountRef
        set folderList to folders of currentAccount

        repeat with folderRef in folderList
            set currentFolder to contents of folderRef

            if (name of currentFolder) is "{folder_name}" then

                set noteList to notes of currentFolder

                repeat with noteRef in noteList
                    set currentNote to contents of noteRef

                    if (name of currentNote) is "{note_name}" then
                        show currentNote
                        activate
                        return "success"
                    end if
                end repeat

            end if
        end repeat
    end repeat

    return "not_found"
end tell
'''

    return run_script(script)



def show_notes_interactive(get_input):
    folder = get_input(
        "Which folder should I search in? Say 'all' for every folder."
    )

    notes = get_notes(folder)

    if not notes:
        return "I couldn't find any notes in that folder."

    print("Assistant: Notes:")

    current_folder = None

    for note in notes:

        if note["folder"] != current_folder:
            current_folder = note["folder"]

            if note["deleted"]:
                print(f"\n[{current_folder} - DELETED]")
            else:
                print(f"\n[{current_folder}]")

        print(f"  - {note['name']}")

    return "Those are the notes I found."



def find_note_interactive(get_input):
    folder = get_input(
        "Which folder should I search in? Say 'all' for every folder."
    )

    name = get_input(
        "Which note should I find?"
    )

    matches = find_notes(name, folder)

    if not matches:
        return f"I couldn't find a note called '{name}'."

    if len(matches) > 1:

        print("Assistant: I found multiple notes:")

        for note in matches:
            status = " - DELETED" if note["deleted"] else ""
            print(
                f"  - [{note['folder']}] "
                f"{note['name']}{status}"
            )

        return "Please specify the folder."

    note = matches[0]

    body = get_note_body(
        note["name"],
        note["folder"]
    )

    status = " - DELETED" if note["deleted"] else ""

    print(
        f"\n[{note['folder']}] "
        f"{note['name']}{status}"
    )

    print(body)
    print()

    return f"Found '{note['name']}'."



def append_note_interactive(get_input):
    folder = get_input(
        "Which folder is the note in?"
    )

    name = get_input(
        "Which note should I add to?"
    )

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
        print("Assistant: I found multiple matching notes:")

        for note in active_matches:
            print(
                f"  - [{note['folder']}] "
                f"{note['name']}"
            )

        return "Please specify the folder."

    text = get_input(
        "What should I add to the note?"
    )

    if not text:
        return "I didn't get anything to add."

    result = append_note(
        name,
        folder,
        text
    )

    if result == "success":
        return f"Added to '{name}'."

    if result == "deleted":
        return "I can't modify notes in Recently Deleted."

    if result == "multiple":
        return "I found multiple matching notes. Please specify the folder."

    return f"I couldn't modify '{name}'."



def delete_note_interactive(get_input):
    folder = get_input(
        "Which folder is the note in?"
    )

    name = get_input(
        "Which note should I delete?"
    )

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
        print("Assistant: I found multiple matching notes:")

        for note in active_matches:
            print(
                f"  - [{note['folder']}] "
                f"{note['name']}"
            )

        return "Please specify the folder."

    result = delete_note(
        name,
        folder
    )

    if result == "success":
        return f"Deleted '{name}'."

    if result == "deleted":
        return "I can't modify notes in Recently Deleted."

    if result == "multiple":
        return "I found multiple matching notes. Please specify the folder."

    return f"I couldn't delete '{name}'."



def open_note_interactive(get_input):
    folder = get_input(
        "Which folder is the note in? Say 'all' for every folder."
    )

    name = get_input(
        "Which note should I open?"
    )

    matches = find_notes(name, folder)

    if not matches:
        return f"I couldn't find a note called '{name}'."

    if len(matches) > 1:

        print("Assistant: I found multiple notes:")

        for note in matches:
            status = " - DELETED" if note["deleted"] else ""

            print(
                f"  - [{note['folder']}] "
                f"{note['name']}{status}"
            )

        return "Please specify the folder."

    result = open_note(
        name,
        matches[0]["folder"]
    )

    if result == "success":
        return f"Opening '{name}'."

    if result == "deleted":
        return "I can't open notes in Recently Deleted."

    return f"I couldn't open '{name}'."
