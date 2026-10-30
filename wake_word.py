import logging

logging.getLogger().setLevel(logging.ERROR)

import os
import numpy as np
import sounddevice as sd
from openwakeword.model import Model


MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "models",
    "hey_jarvis.onnx"
)

model = Model(
    wakeword_models=[MODEL_PATH]
)

SAMPLE_RATE = 16000
CHUNK_SIZE = 1280


def wait_for_wake_word():
    model.reset()

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="int16",
        blocksize=CHUNK_SIZE
    ) as stream:

        while True:
            audio, overflowed = stream.read(CHUNK_SIZE)

            audio = np.squeeze(audio)

            prediction = model.predict(audio)

            score = prediction.get("hey_jarvis", 0)

            if score > 0.8:
                return True
