from ollama import chat
from notes import create_note

def create_note_tool(name: str, body: str, folder: str = "default") -> str:
    """Create a note in Apple Notes.

    Args:
        name: The title of the note.
        body: The content of the note.
        folder: The folder to put the note in. Use default if none is specified.

    Returns:
        The result of the note creation.
    """
    if folder.lower() in ["default", "none"]:
        folder = None

    result = create_note(name, body, folder)

    if result == "folder_not_found":
        return f"Folder '{folder}' was not found."

    if result.startswith("success"):
        return f"Note '{name}' was created successfully."

    return f"Could not create note '{name}'."

tools = [create_note_tool]

messages = [
    {
        "role": "user",
        "content": "Create a note called AI Test and put hello world in it."
    }
]

response = chat(
    model="qwen3:8b",
    messages=messages,
    tools=tools,
    think=False
)

messages.append(response.message)

if response.message.tool_calls:
    for call in response.message.tool_calls:
        if call.function.name == "create_note_tool":
            result = create_note_tool(**call.function.arguments)

            messages.append({
                "role": "tool",
                "tool_name": call.function.name,
                "content": result
            })

    final_response = chat(
        model="qwen3:8b",
        messages=messages,
        tools=tools,
        think=False
    )

    print(f"\nAssistant: {final_response.message.content}")

else:
    print(f"\nAssistant: {response.message.content}")