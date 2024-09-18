import os
import sys

import tqdm
from dotenv import load_dotenv

from core.file_man import get_all_mp3
from core.segment_man import SegmentManager
from core.speech import SpeechRecognition
from core.splitter import load_audio_file, split_file

load_dotenv()

AUDIO_SOURCE_PATH = os.environ.get('AUDIO_SOURCE_PATH')

sr = SpeechRecognition()


def fill_text_for(metadata: SegmentManager, audio=None):
    audio_file = audio or load_audio_file(metadata.original_filename)

    lonely_segments = metadata.segments_without_text
    print(f"Processing {metadata.original_filename}, it has {len(lonely_segments)} segments without text")

    for key, segment in lonely_segments.items():
        start, end = segment['start'], segment['end']

        segment = audio_file[start:end]
        text = sr.recognize(segment)

        text = text.strip()
        if not text.endswith('。') and len(text) >= 5:
            text += '。'
    
        print(f"Recognized: {text} ({len(text) = }) for {start}..{end}")
        metadata.set_segment(start, end, text)
        metadata.save()


def process_one_mp3_file_to_segments(file_path):
    audio_file = load_audio_file(file_path)

    metadata = SegmentManager(file_path)
    metadata.load()

    if not metadata.segments:
        split_file(audio_file, metadata)
        metadata.save()

    fill_text_for(metadata)


def process_all_mp3_files_to_segments(path=AUDIO_SOURCE_PATH):
    all_mp3 = get_all_mp3(path)
    print(f"Found {len(all_mp3)} mp3 files in {path}")
    for mp3 in tqdm.tqdm(all_mp3):
        process_one_mp3_file_to_segments(mp3)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        process_all_mp3_files_to_segments()
    else:
        process_one_mp3_file_to_segments(sys.argv[1])
