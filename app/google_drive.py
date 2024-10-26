from google.oauth2 import service_account
from googleapiclient.discovery import build

drive_service = None


async def init_google_drive():
    global drive_service
    credentials_path = "./propane-cooler-392900-b9458cb8b321.json"  # Replace with actual file path
    scopes = ['https://www.googleapis.com/auth/drive.file']

    credentials = service_account.Credentials.from_service_account_file(
        credentials_path, scopes=scopes)

    drive_service = build('drive', 'v3', credentials=credentials)
    print("Google Drive service initialized")


async def close_google_drive():
    global drive_service
    drive_service = None
    print("Google Drive service closed")

async def get_google_drive():
    return drive_service