# Desktop Assistant

Desktop Assistant is a macOS voice- and text-controlled assistant for common desktop tasks. It uses a local Ollama model to interpret requests, an included wake-word model to listen for “Hey Jarvis,” and focused Python tools for Apple Notes and application control.

## Features

- Voice activation with the included `hey_jarvis.onnx` wake-word model.
- Microphone transcription using OpenAI Whisper’s local `small` model.
- Typed command input in the terminal.
- Local language-model tool selection with Ollama and `qwen3:8b`.
- Apple Notes actions: list, find, read, create, append, open, and delete notes.
- Desktop utilities for opening, quitting, or closing applications and showing or hiding desktop icons.
- Date and time responses through the assistant’s tools.

## Technology

| Technology | Use |
| --- | --- |
| Python 3 | Assistant orchestration and tool functions |
| Ollama (`qwen3:8b`) | Local language model and tool calls |
| `openwakeword` | Wake-word detection |
| `openai-whisper` | Local speech transcription |
| `sounddevice`, `numpy` | Microphone capture and audio processing |
| `certifi` | Certificate bundle used for model downloads |
| AppleScript via `osascript` | Apple Notes and macOS app automation |
| `unittest` | Notes feature tests |

## Requirements

- macOS with Apple Notes, a working microphone, and permissions to control Notes and other apps.
- Python 3.10 or newer.
- [Ollama](https://ollama.com/download) installed and running.
- Disk space and network access for the Ollama model and the first Whisper model download.

## Install and run

From the repository root, create a virtual environment and install the Python packages:

```bash
python3 -m venv .venv
source .venv/bin/activate       # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install ollama openwakeword openai-whisper sounddevice numpy certifi
```

Pull the configured language model and start Ollama if it is not already running:

```bash
ollama pull qwen3:8b
```

Then run the assistant:

```bash
python3 main.py
```

Say **“Hey Jarvis”**, wait for the wake-word prompt, and speak a request, or type a request at the terminal prompt. Enter `exit` or `quit assistant` to stop. The first voice transcription downloads Whisper’s `small` model if it is not already available.

## Project layout

```text
main.py                       Starts voice and keyboard listeners and routes requests
ai.py                         Ollama conversation, tool schemas, and tool dispatch
wake_word.py                  Microphone wake-word detection
voice.py                      Audio capture and Whisper transcription
notes.py                      Apple Notes actions using AppleScript
presets.py                    Application, desktop, date, and time tools
models/hey_jarvis.onnx        Included wake-word model used by the app
models/                       Other included wake-word model files
test_notes_feature.py         Tests for Notes-related behavior
gemini_test.py                Separate Gemini experiment; not used by main.py
ollama_test.py                Separate Ollama experiment
main_backup.py                Backup copy of the main entry point
```

## Permissions and privacy

Speech audio is captured by the microphone and transcribed locally by Whisper. The language model is served locally by Ollama. Apple Notes and application-control actions use macOS automation permissions. Review commands carefully when they modify or delete Notes content. This is a local personal project, not a hardened multi-user service.

## Tests

Run the existing Notes-related tests with:

```bash
python3 -m unittest test_notes_feature.py
```

## Sources

- [Ollama documentation](https://docs.ollama.com/)
- [Qwen 3 model on Ollama](https://ollama.com/library/qwen3)
- [OpenAI Whisper repository](https://github.com/openai/whisper)
- [openWakeWord repository](https://github.com/dscripka/openWakeWord)
- [python-sounddevice documentation](https://python-sounddevice.readthedocs.io/)
- [AppleScript Language Guide](https://developer.apple.com/library/archive/documentation/AppleScript/Conceptual/AppleScriptX/)
