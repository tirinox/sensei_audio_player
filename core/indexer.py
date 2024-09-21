import json
import os.path

from core.file_man import get_all_mp3
from core.segment_man import SegmentManager


class AudioIndexer:
    def __init__(self, path):
        self.path = path
        self.files = []

    @property
    def index_file(self):
        return os.path.join(self.path, 'index.json')

    def scan_files(self):
        all_mp3 = get_all_mp3(self.path)
        if not all_mp3:
            print("No mp3 found! Check your path")
            return

        files = []

        for mp3_file in all_mp3:
            seg = SegmentManager(mp3_file)
            if seg.load():
                just_filename = os.path.basename(mp3_file)
                files.append({
                    "audio_file": just_filename,
                    "segment_file": seg.segments_filename(just_filename),
                    "n_segments": len(seg.segments),
                    "length": len(seg.audio) / 1000,
                    "title": just_filename,
                })

        return files

    def rebuild_index_and_save(self):
        self.files = self.scan_files()
        # todo: preserve title if it's already in the index
        self.save()

    def save(self):
        index = {
            'path': self.path,
            'files': self.files,
        }
        with open(self.index_file, 'w') as f:
            json.dump(index, f, indent=4, ensure_ascii=False)

    def load_index(self, allow_rebuild=False):
        if not os.path.exists(self.index_file):
            if allow_rebuild:
                return self.rebuild_index_and_save()

        with open(self.index_file, 'r') as f:
            index = json.load(f)
            self.path = index['path']
            self.files = index['files']

    def __getitem__(self, item):
        return self.files[item]

    def find_by_audio_file(self, search):
        for file in self.files:
            if search in file['audio_file']:
                return os.path.join(self.path, file['audio_file'])

    def sort_files(self):
        self.files.sort(key=lambda x: x['audio_file'])
        return self.files
