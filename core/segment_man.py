import json


class SegmentManager:
    @staticmethod
    def segments_filename(original_filename):
        return original_filename + "_segments.json"

    def __init__(self, filename):
        self._filename = filename
        self.segments = {}

    @property
    def sorted_segments(self):
        return sorted(self.segments.values(), key=lambda x: x['start'])

    @property
    def original_filename(self):
        return self._filename

    def save(self):
        json_filename = self.segments_filename(self._filename)
        with open(json_filename, "w") as json_file:
            json.dump({
                "filename": self._filename,
                "total_segments": len(self.segments),
                "segments": self.segments,
                "version": 2
            }, json_file, ensure_ascii=False, indent=4)
        print(f"Non-silent segments saved to {json_filename}")

    def load(self):
        json_filename = self.segments_filename(self._filename)
        self.segments = {}
        try:
            with open(json_filename, "r") as json_file:
                data = json.load(json_file)
                version = data.get('version', 1)
                if version != 2:
                    raise ValueError(f"Unsupported version: {version}")

                self.segments = data['segments']
                self._filename = data['filename']
            print(f"Non-silent segments loaded from {json_filename}")
            return True
        except FileNotFoundError:
            print(f"Non-silent segments JSON file not found: {json_filename}")
            return False

    @staticmethod
    def segment_key(start, end):
        return f'{start:08}..{end:08}'

    def set_segment(self, start, end, text=''):
        self.segments[self.segment_key(start, end)] = {
            'start': start,
            'end': end,
            'text': text
        }

    def does_segment_exist(self, start, end):
        return self.segment_key(start, end) in self.segments

    @property
    def segments_without_text(self):
        return {k: v for k, v in self.segments.items() if not v['text']}
