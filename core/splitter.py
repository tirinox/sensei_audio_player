from pydub import AudioSegment
from pydub.silence import detect_silence


def detect_pieces(audio, padding=100):
    # Detect silence longer than 1000 ms (1 second)
    print("Detecting silence...")

    silences = detect_silence(audio, min_silence_len=1000, silence_thresh=-40)

    if not silences:
        silences = [[0, len(audio)]]

    # Generate a list of non-silent segments
    non_silent_segments = []
    start = 0
    for silence_start, silence_end in silences:
        # Add padding to the non-silent segments
        silence_start = max(0, silence_start - padding)
        silence_end = min(len(audio), silence_end + padding)

        if start < silence_start:
            non_silent_segments.append((start, silence_start))
        start = silence_end

    # Add the final segment if there's remaining audio after the last silence
    if start < len(audio):
        non_silent_segments.append((start, len(audio)))

    # Display the non-silent segments and let the user select one to play
    print("Non-silent segments available:")
    for idx, (start, end) in enumerate(non_silent_segments):
        print(
            f"{idx}: From {start / 1000:.2f} seconds to {end / 1000:.2f} seconds, duration: {(end - start) / 1000:.2f} seconds")
    return non_silent_segments


def load_audio_file(file_path):
    return AudioSegment.from_mp3(file_path)
