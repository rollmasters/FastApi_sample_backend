import json

import requests

import os


def send_request(url, file_path=None, lang=None, user_messages=None, payload=None):
    if file_path:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Prepare multipart/form-data with file and additional fields
        with open(file_path, 'rb') as f:
            user_messages_str = json.dumps(user_messages) if user_messages else None
            files = {
                'wavData': ('output.wav', f, 'audio/wav')  # File to upload
            }
            data = {
                'lang': lang,  # Form data fields
                'user_messages': user_messages_str  # Ensure this is a string
            }

            response = requests.post(url, files=files, data=data)
            response.raise_for_status()
            return response.json()

            response = requests.post(url, files=form_data)
            response.raise_for_status()
            return response.json()

    elif payload:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()

    else:
        raise ValueError("Either file_path or payload must be provided")
