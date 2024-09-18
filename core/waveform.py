import numpy as np
from PIL import Image, ImageDraw


def audio_to_waveform_png(audio_clip, output_path="waveform.png", width=800, height=60, smoothing_window=5):
    # Convert pydub audio clip to raw data (samples)
    samples = np.array(audio_clip.get_array_of_samples())

    # Downsample the audio to fit within the desired width (800 pixels)
    downsampled_samples = samples[::len(samples) // width]  # Resample to 800 points

    # Apply logarithmic scaling on the amplitude
    max_amplitude = np.max(np.abs(downsampled_samples))
    log_amplitudes = np.log1p(np.abs(downsampled_samples)) / np.log1p(max_amplitude)

    # Normalize the amplitude to fit within the desired height (60 pixels)
    normalized_samples = log_amplitudes * (height // 2 - 1)  # Normalize to half the height

    # Apply a simple moving average for smoothing
    smoothed_samples = np.convolve(normalized_samples, np.ones(smoothing_window) / smoothing_window, mode='same')

    # Create a white image (800x60) with Pillow
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)

    # Draw the waveform: Black line representing the amplitude
    midline = height // 2  # Middle of the height
    for x in range(width):
        amplitude = smoothed_samples[x]
        draw.line([(x, midline - amplitude), (x, midline + amplitude)], fill="black")

    # Save the image as PNG
    img.save(output_path)
