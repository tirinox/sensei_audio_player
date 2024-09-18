from dotenv import load_dotenv

from core.config import AUDIO_SOURCE_PATH
from core.indexer import AudioIndexer
from core.player import Player
from core.segment_man import SegmentManager
from core.speech import SpeechRecognition
from core.splitter import load_audio_file, split_file
from core.utils import au_sep
from core.waveform import audio_to_waveform_png
from process_segments import fill_text_for

load_dotenv()

indexer = AudioIndexer(AUDIO_SOURCE_PATH)
indexer.load_index()


def force_split_and_play_in_loop(query='相撲'):
    example = indexer.find_by_audio_file(query)
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


def force_speech_recognition(query='ここはどこですか'):
    # example = indexer.find_by_audio_file('相撲')
    example = indexer.find_by_audio_file(query)
    if not example:
        print("Example not found.")
        return

    audio_file = load_audio_file(example)
    metadata = SegmentManager(example)
    # if True:
    if not metadata.load():
        split_file(audio_file, metadata)
        metadata.save()

    fill_text_for(metadata, audio=audio_file)


def have_fun_waveform(query='ここはどこですか'):
    example = indexer.find_by_audio_file(query)
    if not example:
        print("Example not found.")
        return

    player = Player(example)
    _, _, piece = player[5]

    # audio_to_waveform_png(piece)
    # player.play_segment(5)

    audio_to_waveform_png(player.audio)



have_fun_waveform()
# force_speech_recognition()
# force_split_and_play_in_loop(query='ここはどこですか')
