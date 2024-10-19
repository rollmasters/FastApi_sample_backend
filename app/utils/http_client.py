import aiohttp

import requests
import json
import os

def send_request(url, file_path=None, lang=None, user_messages=None, payload=None):
    if file_path:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Prepare multipart/form-data with file
        with open(file_path, 'rb') as f:
            files = {
                'file': ('output.wav', f, 'audio/wav')
            }
            data = {
                'lang': lang,
                'user_messages': json.dumps(user_messages)
            }

            response = requests.post(url, files=files, data=data)
            response.raise_for_status()
            return response.json()

    elif payload:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()

    else:
        raise ValueError("Either file_path or payload must be provided")
