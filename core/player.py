from pydub.playback import play


class Player:
    def __init__(self, audio, segments):
        self.audio = audio
        self._segments = segments
        self.current_segment_idx = 0

    def __getitem__(self, item):
        start, end = self._segments[item]
        segment = self.audio[start:end]
        return start, end, segment

    def play_segment(self, idx):
        start, end, segment = self[idx]
        print(f"[{idx:02} / {len(self._segments):02}] Playing segment "
              f"from {start / 1000:.2f} seconds to {end / 1000:.2f} seconds...")
        play(segment)

    def play_current_segment(self):
        self.play_segment(self.current_segment_idx)

    def play_next_segment(self):
        self.current_segment_idx += 1
        self.current_segment_idx %= len(self._segments)
        self.play_current_segment()

    def play_previous_segment(self):
        self.current_segment_idx -= 1
        self.current_segment_idx %= len(self._segments)
        self.play_current_segment()
