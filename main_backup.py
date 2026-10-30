import os
import sys
import threading
import queue

from ai import process
from voice import listen
from wake_word import wait_for_wake_word


input_queue = queue.Queue()
shutdown_event = threading.Event()
prompt_ready = threading.Event()


def restart_assistant():
    os.execv(
        sys.executable,
        [sys.executable] + sys.argv
    )


def voice_listener():
    while not shutdown_event.is_set():
        print("Voice: Waiting for 'Hey Jarvis'...")

        wait_for_wake_word()

        if shutdown_event.is_set():
            break

        print("Voice: Wake word detected. Listening...")

        command = listen()

        if command:
            input_queue.put(
                ("voice", command)
            )


def keyboard_listener():
    while not shutdown_event.is_set():
        prompt_ready.wait()

        if shutdown_event.is_set():
            break

        try:
            command = input("> ").strip()

        except EOFError:
            shutdown_event.set()
            break

        prompt_ready.clear()

        if command:
            input_queue.put(
                ("text", command)
            )
        else:
            prompt_ready.set()


def get_next_input():
    return input_queue.get()


def display_command(source, command):
    if source == "voice":
        print(f"> {command}")


def handle_special_commands(command):
    normalized = command.strip().lower().strip(" .!?")

    if normalized == "exit":
        return "exit"

    if normalized == "quit assistant":
        return "exit"

    if normalized == "shutdown assistant":
        return "exit"

    if normalized == "restart":
        print("Restarting assistant...", flush=True)
        restart_assistant()

    return None


def main():
    print("---------------------------------------")
    print("           Desktop Assistant")
    print("---------------------------------------")
    print()
    print("Voice: Say 'Hey Jarvis'")
    print("Text: Type a command, then press Enter")
    print("Status: Ready")
    print()

    prompt_ready.set()

    threading.Thread(
        target=voice_listener,
        daemon=True
    ).start()

    threading.Thread(
        target=keyboard_listener,
        daemon=True
    ).start()

    while not shutdown_event.is_set():
        source, command = get_next_input()

        display_command(source, command)

        special_command = handle_special_commands(command)

        if special_command == "exit":
            shutdown_event.set()

            print("Assistant terminated!")

            break

        try:
            response = process(command)

        except Exception as e:
            response = f"AI error: {e}"

        print(
            f"Assistant: {response}"
        )

        print()

        prompt_ready.set()


if __name__ == "__main__":
    main()