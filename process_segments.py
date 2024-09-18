import os

import tqdm
from dotenv import load_dotenv

from core.file_man import get_all_mp3
from core.segment_man import SegmentManager
from core.speech import SpeechRecognition
from core.splitter import load_audio_file, detect_pieces

load_dotenv()

AUDIO_SOURCE_PATH = os.environ.get('AUDIO_SOURCE_PATH')

sr = SpeechRecognition()


def fill_text_for(metadata: SegmentManager):
    audio_file = load_audio_file(metadata.original_filename)

    # audio_file = prepare_audio_for_recognition(audio_file)

    lonely_segments = metadata.segments_without_text
    print(f"Processing {metadata.original_filename}, it has {len(lonely_segments)} segments without text")

    for key, segment in lonely_segments.items():
        start, end = segment['start'], segment['end']

        segment = audio_file[start:end]
        text = sr.recognize(segment)
        # text = recognize_japanese_speech(audio_file, start, end)
        print(f"Recognized: {text} for {start}..{end}")
        metadata.set_segment(start, end, text)

    metadata.save()


def process_one_mp3_file_to_segments(file_path):
    audio_file = load_audio_file(file_path)

    metadata = SegmentManager(file_path)
    metadata.load()

    if not metadata.segments:
        non_silent_segments = detect_pieces(audio_file)
        for idx, (start, end) in enumerate(non_silent_segments):
            if not metadata.does_segment_exist(start, end):
                metadata.set_segment(start, end, "")
        metadata.save()

    fill_text_for(metadata)


def process_all_mp3_files_to_segments(path=AUDIO_SOURCE_PATH):
    all_mp3 = get_all_mp3(path)
    print(f"Found {len(all_mp3)} mp3 files in {path}")
    for mp3 in tqdm.tqdm(all_mp3):
        process_one_mp3_file_to_segments(mp3)


if __name__ == '__main__':
    process_all_mp3_files_to_segments()
