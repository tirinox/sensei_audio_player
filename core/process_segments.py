import os

from dotenv import load_dotenv
from tqdm import tqdm

from core.segment_man import SegmentManager
from core.speech import SpeechRecognitionWhisper
from core.splitter import load_audio_file

load_dotenv()

AUDIO_SOURCE_PATH = os.environ.get('AUDIO_SOURCE_PATH')

g_sr = None


def fill_text_for(metadata: SegmentManager, audio=None, sr=None, skip_existing=True):
    global g_sr
    if not sr:
        if not g_sr:
            g_sr = SpeechRecognitionWhisper()
            # g_sr = SpeechRecognitionGoogle()
        sr = g_sr

    audio_file = audio or load_audio_file(metadata.original_filename)

    lonely_segments = metadata.segments_without_text
    print(f"Processing {metadata.original_filename}, it has {len(lonely_segments)} segments without text")

    for key, segment in tqdm(lonely_segments.items()):
        start, end = segment['start'], segment['end']

        if segment.get('text') and skip_existing:
            print(f"Skipping existing segment {start}..{end}")
            continue

        segment = audio_file[start:end]
        text = sr.recognize(segment)
        if text is None:
            print(f"Failed to recognize speech for {start}..{end}")
            continue

        text = text.strip()

        text = text.replace('か?', 'か。')

        if not text.endswith('。') and not text.endswith('？') and not text.endswith('?') and len(text) >= 5:
            text += '。'

        print(f"Recognized: {text} ({len(text) = }) for {start}..{end}")
        metadata.set_segment(start, end, text)
        metadata.save()
