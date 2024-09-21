import io
import os
from urllib.error import URLError

import numpy as np
import speech_recognition as sr
from pydub import AudioSegment
from speech_recognition import AudioData, RequestError, UnknownValueError
import whisper


def prepare_audio_for_recognition(audio):
    if audio.frame_rate != 16000:  # 16 kHz
        audio = audio.set_frame_rate(16000)
    if audio.sample_width != 2:  # int16
        audio = audio.set_sample_width(2)
    if audio.channels != 1:  # mono
        audio = audio.set_channels(1)
    return audio


class SpeechRecognitionWhisper:
    def __init__(self):
        self.model = whisper.load_model("large")

    # Old whisper code
    def recognize_japanese_speech_whisper(self, audio):
        # Prepare the audio for recognition
        audio = prepare_audio_for_recognition(audio)

        arr = np.array(audio.get_array_of_samples())
        arr = arr.astype(np.float32) / 32768.0

        result = self.model.transcribe(arr, language="ja")

        # Return the recognized text
        return result["text"]


class SpeechRecognitionGoogle:
    def __init__(self, language="ja-JP"):
        self.recognizer = MyRecognizer()
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
                text = self.recognizer.recognize_google_cloud(audio_data, language=self.language, )
                print("Transcription: ", text)
                return text
            except sr.UnknownValueError:
                print("Google Web Speech API could not understand the audio")
            except sr.RequestError as e:
                print(f"Could not request results from Google Web Speech API; {e}")


class MyRecognizer(sr.Recognizer):
    def recognize_google_cloud(self, audio_data, credentials_json=None, language="en-US", preferred_phrases=None,
                               show_all=False):
        assert isinstance(audio_data, AudioData), "``audio_data`` must be audio data"
        if credentials_json is None:
            assert os.environ.get('GOOGLE_APPLICATION_CREDENTIALS') is not None
        assert isinstance(language, str), "``language`` must be a string"
        assert preferred_phrases is None or all(
            isinstance(preferred_phrases, (type(""), type(u""))) for preferred_phrases in
            preferred_phrases), "``preferred_phrases`` must be a list of strings"

        try:
            import socket

            from google.api_core.exceptions import GoogleAPICallError
            from google.cloud import speech
        except ImportError:
            raise RequestError(
                'missing google-cloud-speech module: ensure that google-cloud-speech is set up correctly.')

        if credentials_json is not None:
            client = speech.SpeechClient.from_service_account_json(credentials_json)
        else:
            client = speech.SpeechClient()

        flac_data = audio_data.get_flac_data(
            convert_rate=None if 8000 <= audio_data.sample_rate <= 48000 else max(8000,
                                                                                  min(audio_data.sample_rate, 48000)),
            # audio sample rate must be between 8 kHz and 48 kHz inclusive - clamp sample rate into this range
            convert_width=2  # audio samples must be 16-bit
        )
        audio = speech.RecognitionAudio(content=flac_data)

        config = {
            'encoding': speech.RecognitionConfig.AudioEncoding.FLAC,
            'sample_rate_hertz': audio_data.sample_rate,
            'language_code': language,
            'enable_automatic_punctuation': True,  # <-----
        }
        if preferred_phrases is not None:
            config['speechContexts'] = [speech.SpeechContext(
                phrases=preferred_phrases
            )]
        if show_all:
            config['enableWordTimeOffsets'] = True  # some useful extra options for when we want all the output

        opts = {}
        if self.operation_timeout and socket.getdefaulttimeout() is None:
            opts['timeout'] = self.operation_timeout

        config = speech.RecognitionConfig(**config)

        try:
            response = client.recognize(config=config, audio=audio)
        except GoogleAPICallError as e:
            raise RequestError(e)
        except URLError as e:
            raise RequestError("recognition connection failed: {0}".format(e.reason))

        if show_all: return response
        if len(response.results) == 0:
            raise UnknownValueError()

        transcript = ''
        for result in response.results:
            transcript += result.alternatives[0].transcript.strip() + ' '
        return transcript
