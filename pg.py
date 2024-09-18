import os.path

from dotenv import load_dotenv

from core.config import AUDIO_SOURCE_PATH
from core.indexer import AudioIndexer
from core.segment_man import SegmentManager
from core.speech import recognize_japanese_speech
from core.splitter import load_audio_file

load_dotenv()

indexer = AudioIndexer(AUDIO_SOURCE_PATH)
index = indexer.load_index()
example = index['files'][5]
print(example)

audio_file_path = os.path.join(AUDIO_SOURCE_PATH, example['audio_file'])
segments = SegmentManager(audio_file_path)
segments.load()

print(segments.segments)

example_segment = list(segments.segments.values())[1]
print(example_segment)

audio = load_audio_file(audio_file_path)

r = recognize_japanese_speech(audio, example_segment['start'], example_segment['end'])
print(r)