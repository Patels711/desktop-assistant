import ssl
import certifi
import whisper
import sounddevice as sd
import numpy as np


ssl._create_default_https_context = lambda: ssl.create_default_context(
    cafile=certifi.where()
)


model = None


def load_model():
    global model

    if model is None:
        model = whisper.load_model("small")


def listen(duration=4):
    load_model()

    sample_rate = 16000

    audio = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype="float32"
    )

    sd.wait()

    audio = np.squeeze(audio)

    if np.max(np.abs(audio)) > 0:
        audio = audio / np.max(np.abs(audio))

    result = model.transcribe(
        audio,
        fp16=False,
        language="en",
        temperature=0,
        condition_on_previous_text=False
    )

    return result["text"].strip()


if __name__ == "__main__":
    command = listen()
    print(f"You said: {command}")
