import json
import os.path

from code.file_man import get_all_mp3
from code.segment_man import SegmentManager


class AudioIndexer:
    def __init__(self, path):
        self.path = path

    @property
    def index_file(self):
        return os.path.join(self.path, 'index.json')

    def build_index(self):
        all_mp3 = get_all_mp3(self.path)
        if not all_mp3:
            print("No mp3 found! Check your path")
            return

        files = []

        for mp3_file in all_mp3:
            seg = SegmentManager(mp3_file)
            if seg.load():
                mp3_file_name = os.path.basename(mp3_file)
                files.append({
                    "audio_file": mp3_file_name,
                    "segment_file": seg.segments_filename(mp3_file_name),
                    "n_segments": len(seg.segments),
                })

        return {
            "dir": self.path,
            "files": files
        }

    def rebuild_index_and_save(self):
        index = self.build_index()
        with open(self.index_file, 'w') as f:
            json.dump(index, f, indent=4, ensure_ascii=False)
        return index

    def load_index(self, allow_rebuild=False):
        if not os.path.exists(self.index_file):
            if allow_rebuild:
                return self.rebuild_index_and_save()

        with open(self.index_file, 'r') as f:
            return json.load(f)
