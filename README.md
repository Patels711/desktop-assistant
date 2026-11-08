# Desktop Assistant

A macOS voice- and text-controlled assistant that uses a locally hosted language model to help with everyday desktop tasks, including Apple Notes and application control.

## Project goals

Desktop Assistant aims to make common Mac tasks easier to request in natural language while keeping the AI reasoning local. You can speak a command after saying **“Hey Jarvis”** or type it into the terminal. The assistant routes requests to focused tools and reports the result.

## Features

- Voice activation with an included wake-word model.
- Local speech transcription and typed command input.
- Natural-language tool selection using Ollama and `qwen3:8b`.
- Apple Notes actions: list, find, read, create, append to, open, and delete notes.
- Desktop utilities such as opening, quitting, and closing applications, and showing or hiding desktop icons.
- Date and time answers, plus automated tests for Notes-related behavior.

## Technology stack

| Technology | Purpose |
| --- | --- |
| Python 3 | Application and tool orchestration |
| Ollama (`qwen3:8b`) | Local language model and tool calling |
| `openwakeword` | “Hey Jarvis” wake-word detection |
| `openai-whisper` | Speech-to-text transcription |
| `sounddevice`, `numpy` | Microphone input and audio processing |
| AppleScript (`osascript`) | Native Apple Notes and macOS automation |
| `unittest` | Automated tests |

## Requirements

- macOS with Apple Notes and a working microphone.
- Python 3.
- [Ollama](https://ollama.com/) installed and running, with the `qwen3:8b` model available.
- The wake-word model files in the included `models/` directory.
- Python packages used by the project: `ollama`, `openwakeword`, `openai-whisper`, `sounddevice`, `numpy`, and `certifi`.

Install the Python packages in your environment (for example, with `python3 -m pip install ollama openwakeword openai-whisper sounddevice numpy certifi`). Package installation for audio and speech-recognition libraries can vary by macOS and Python version; follow their upstream setup instructions if installation reports missing system dependencies.

## Run

From the repository root, start Ollama and run:

```bash
ollama pull qwen3:8b
python3 main.py
```

Say **“Hey Jarvis”** and then speak a request, or type a command at the prompt. Use `exit` or `quit assistant` to stop the assistant. The first Whisper use may need to download its speech model.

## Safety and privacy notes

The language model runs through local Ollama, but voice input is captured by the microphone and Apple Notes actions make changes in your Notes account. Review requests before using destructive actions such as deleting a note. The app uses macOS automation permissions, so macOS may ask you to authorize access to Notes or other applications.

## Tests

Run the Notes-related tests with:

```bash
python3 -m unittest test_notes_feature.py
```

## Project structure

- `main.py` — voice/keyboard input loop and application entry point.
- `ai.py` — Ollama chat, tool definitions, and request handling.
- `voice.py`, `wake_word.py` — speech capture and wake-word detection.
- `notes.py` — Apple Notes integration.
- `presets.py` — application, desktop, date, and time utilities.
- `models/` — included wake-word models.
- `test_notes_feature.py` — Notes feature tests.

## Limitations

This project is currently designed for macOS and depends on Apple Notes and native AppleScript automation. Voice recognition and model performance depend on the local machine, microphone, and installed model packages.
