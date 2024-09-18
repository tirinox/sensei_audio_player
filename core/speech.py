import io

import numpy as np
import whisper

model = whisper.load_model("large")


def prepare_audio_for_recognition(audio):
    if audio.frame_rate != 16000:  # 16 kHz
        audio = audio.set_frame_rate(16000)
    if audio.sample_width != 2:  # int16
        audio = audio.set_sample_width(2)
    if audio.channels != 1:  # mono
        audio = audio.set_channels(1)
    return audio


def recognize_japanese_speech(audio, start_time, end_time):
    # Extract the segment (pydub works in milliseconds)
    segment = audio[start_time:end_time]

    arr = np.array(segment.get_array_of_samples())
    arr = arr.astype(np.float32) / 32768.0

    result = model.transcribe(arr, language="ja")

    # Return the recognized text
    return result["text"]
