import os


def get_all_mp3(path):
    """
    Get all mp3 files in the specified directory.
    :param path:
    :return:
    """
    mp3_files = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".mp3"):
                mp3_files.append(os.path.join(root, file))
    return mp3_files


def waveform_out_path(original_file_name, index):
    base_name = os.path.basename(original_file_name)
    base_path = os.path.dirname(original_file_name)
    os.makedirs(os.path.join(base_path, 'waveforms', base_name), exist_ok=True)
    return os.path.join(base_path, 'waveforms', base_name, f'wf_{index:03}.png')
