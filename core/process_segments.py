import os

from dotenv import load_dotenv

from core.segment_man import SegmentManager
from core.speech import SpeechRecognitionGoogle
from core.splitter import load_audio_file

load_dotenv()

AUDIO_SOURCE_PATH = os.environ.get('AUDIO_SOURCE_PATH')

sr = SpeechRecognitionGoogle()


def fill_text_for(metadata: SegmentManager, audio=None):
    audio_file = audio or load_audio_file(metadata.original_filename)

    lonely_segments = metadata.segments_without_text
    print(f"Processing {metadata.original_filename}, it has {len(lonely_segments)} segments without text")

    for key, segment in lonely_segments.items():
        start, end = segment['start'], segment['end']

        segment = audio_file[start:end]
        text = sr.recognize(segment)
        if text is None:
            print(f"Failed to recognize speech for {start}..{end}")
            continue

        text = text.strip()
        if not text.endswith('。') and not text.endswith('？') and len(text) >= 5:
            text += '。'

        print(f"Recognized: {text} ({len(text) = }) for {start}..{end}")
        metadata.set_segment(start, end, text)
        metadata.save()
