# Desktop Assistant

A macOS desktop assistant that combines voice control, typed commands, local AI, and Apple Notes automation. Wake it with “Hey Jarvis” or type directly into the terminal, then ask naturally for help with notes, apps, dates, time, or desktop actions.

The assistant uses a local Ollama model (`qwen3:8b`) as its reasoning layer. Instead of requiring exact commands, it interprets natural language and selects the correct tool for the task. For example, it can create, find, append to, delete, list, and open Apple Notes; open, quit, or close supported macOS applications; show or hide desktop icons; and answer date or time requests.

Apple Notes support is designed with safety in mind. The assistant can search across folders, recognize aliases such as “all notes” or “college notes,” identify duplicate note names, and clearly show which folders contain matching notes. Notes in Recently Deleted are labeled and protected from modification or opening. When no folder is specified during note creation, Apple Notes uses the user’s configured default location.

Voice support uses an on-device wake-word model and speech transcription. The terminal displays assistant status, wake-word detection, recognized voice commands, typed commands, and responses in a simple readable format. Voice and text input can be mixed during multi-step note workflows.

## Key Libraries

- `ollama` — local AI chat and tool calling with `qwen3:8b`
- `openwakeword` — custom “Hey Jarvis” wake-word detection
- `openai-whisper` — local speech-to-text transcription
- `sounddevice` — microphone recording and audio input streams
- `numpy` — audio buffer processing
- `certifi` — SSL certificate support for Whisper downloads
- `subprocess` + `osascript` — native macOS AppleScript automation
- `unittest` — automated Notes command and safety tests
- `google-genai` — experimental Gemini connectivity test

## Requirements

- macOS with Apple Notes installed and accessible
- Python 3
- Ollama running locally with the `qwen3:8b` model installed
- A working microphone
- The included wake-word model in `models/`

Run the assistant with:

```bash
python3 main.py
