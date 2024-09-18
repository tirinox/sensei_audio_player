import os.path
from time import sleep

from dotenv import load_dotenv

from core.config import AUDIO_SOURCE_PATH
from core.indexer import AudioIndexer
from core.player import Player
from core.segment_man import SegmentManager
from core.splitter import load_audio_file, split_file
from core.utils import au_sep

load_dotenv()

indexer = AudioIndexer(AUDIO_SOURCE_PATH)
indexer.load_index()

example = indexer.find_by_audio_file('相撲')
print(example)

player = Player(example)

player.ready = False
if not player.ready:
    print("Failed to load segments. Splitting the file.")
    split_file(player.audio, player.metadata)
    player.metadata.save()

while True:
    player.play_current_segment()

    au_sep()

    player.shift(1)

# audio_file_path = os.path.join(AUDIO_SOURCE_PATH, example['audio_file'])
# segments = SegmentManager(audio_file_path)
# segments.load()
#
# print(segments.segments)

# example_segment = list(segments.segments.values())[1]
# print(example_segment)

# audio = load_audio_file(audio_file_path)
#
