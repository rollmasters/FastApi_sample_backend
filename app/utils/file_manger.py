import os

def save_audio_file(audio_data):
    file_path = "output.wav"
    with open(file_path, "wb") as f:
        f.write(audio_data)
    return file_path