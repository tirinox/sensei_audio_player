import io

import speech_recognition as sr
# import whisper
from pydub import AudioSegment


# model = whisper.load_model("large")


def prepare_audio_for_recognition(audio):
    if audio.frame_rate != 16000:  # 16 kHz
        audio = audio.set_frame_rate(16000)
    if audio.sample_width != 2:  # int16
        audio = audio.set_sample_width(2)
    if audio.channels != 1:  # mono
        audio = audio.set_channels(1)
    return audio


## Old whisper code
# def _recognize_japanese_speech_whisper(audio, start_time, end_time):
#     # Extract the segment (pydub works in milliseconds)
#     segment = audio[start_time:end_time]
#
#     arr = np.array(segment.get_array_of_samples())
#     arr = arr.astype(np.float32) / 32768.0
#
#     result = model.transcribe(arr, language="ja")
#
#     # Return the recognized text
#     return result["text"]


class SpeechRecognition:
    def __init__(self, language="ja-JP"):
        self.recognizer = sr.Recognizer()
        self.language = language

    def recognize(self, piece: AudioSegment):
        wav_io = io.BytesIO()
        piece.export(wav_io, format="wav")
        wav_io.seek(0)

        with sr.AudioFile(wav_io) as source:
            print(f"Recognizing a piece of audio length {len(piece) / 1000:.2f} seconds...")
            audio_data = self.recognizer.record(source)  # Read the entire audio file
            try:
                # Recognize speech using Google Web Speech API, set language to Japanese (ja-JP)
                text = self.recognizer.recognize_google_cloud(audio_data, language=self.language)
                print("Transcription: ", text)
                return text
            except sr.UnknownValueError:
                print("Google Web Speech API could not understand the audio")
            except sr.RequestError as e:
                print(f"Could not request results from Google Web Speech API; {e}")
