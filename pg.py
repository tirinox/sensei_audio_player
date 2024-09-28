import os.path
import sys

from dotenv import load_dotenv

from core.config import AUDIO_SOURCE_PATH
from core.file_man import waveform_out_path, get_all_mp3
from core.furigana import add_furigana_v2, parentheses_to_ruby_v2
from core.indexer import AudioIndexer
from core.player import Player
from core.process_segments import fill_text_for
from core.segment_man import SegmentManager
from core.splitter import load_audio_file, split_file
from core.utils import au_sep
from core.waveform import audio_to_waveform_png

load_dotenv()

indexer = AudioIndexer(AUDIO_SOURCE_PATH)
try:
    indexer.load_index()
except FileNotFoundError:
    print("Index file not found.")


def force_split_and_play_in_loop(query='相撲'):
    example = get_example()
    print("Processing example:", example)

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


def get_example():
    example = sys.argv[2].strip()

    if example.isdigit():
        print("Example is a number. Trying to find file by index.")
        example = int(example)
        files = get_all_mp3(AUDIO_SOURCE_PATH)
        example = files[example - 1]
    if os.path.dirname(example) == '':
        print("Example is a filename. Trying to find it in the database path.")
        example = os.path.join(AUDIO_SOURCE_PATH, example)
    return example


def force_speech_recognition():
    example = get_example()
    print("Processing example:", example)

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
    index = 5
    _, _, piece = player[index]

    # audio_to_waveform_png(piece)
    # player.play_segment(5)

    audio_to_waveform_png(player.audio, output_path=waveform_out_path(example, index))


def reindex():
    indexer.rebuild_index_and_save()
    indexer.sort_files()
    indexer.save()


def process_incoming():
    main_db_path = AUDIO_SOURCE_PATH
    files = get_all_mp3(main_db_path)
    for file in files:
        basename = os.path.basename(file)
        if not basename.startswith('lb'):
            print(f'Found new file: {basename}')
            basename = basename.replace('-kissvk.com', '')
            basename = basename.replace('My Recording-', '')
            basename = f'lb_{basename}'
            print(f'New name: {basename}')
            os.system(f'ffmpeg -i "{file}" -b:a 128k "{os.path.join(main_db_path, basename)}"')


def list_files():
    main_db_path = AUDIO_SOURCE_PATH
    files = get_all_mp3(main_db_path)
    for i, file in enumerate(files):
        print(f'{i + 1}. {os.path.basename(file)}')


def foo_func():
    f = indexer.files[4]
    print(f)
    seg_manager = SegmentManager(os.path.join(AUDIO_SOURCE_PATH, f['audio_file']))
    seg_manager.load()
    for seg in seg_manager.sorted_segments:
        text = seg['text']
        furi_text = add_furigana_v2(text)
        print('-------')
        print(text)
        print(furi_text)
        html = parentheses_to_ruby_v2(furi_text)
        print(html)


def convert_ruby():
    example = get_example()
    print("Processing example:", example)
    metadata = SegmentManager(example)
    metadata.load()
    metadata.convert_ruby_to_parenthesis()
    print("Converted to parenthesis")
    input("Press Enter to continue...")
    metadata.save()


command_map = {
    'reindex': reindex,
    'waveform': have_fun_waveform,
    'update': force_speech_recognition,
    'split': force_split_and_play_in_loop,
    'process_incoming': process_incoming,
    'list': list_files,
    'foo': foo_func,
    'convert_ruby': convert_ruby,
}

if __name__ == '__main__':
    command = sys.argv[1] if len(sys.argv) > 1 else None
    if not command:
        print("No command provided. Available commands: ", list(command_map.keys()))
        sys.exit(1)

    command = command.strip().lower()
    if command in command_map:
        print("Running command:", command)
        command_map[command]()
    else:
        print("Unknown command. Available commands: ", list(command_map.keys()))
