import os
from google.cloud import storage
from app.core.config import settings  # Import the settings from your config


# Initialize the Google Cloud Storage client
def get_gcs_client():
    """
    Initialize and return a Google Cloud Storage client using the credentials
    set in the configuration file (Settings).
    """
    # Ensure the GOOGLE_APPLICATION_CREDENTIALS environment variable is set
    if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        raise EnvironmentError("GOOGLE_APPLICATION_CREDENTIALS not set in the environment.")

    # Create and return the storage client
    return storage.Client()


def get_file_from_gcs(bucket_name: str, file_path: str, as_text=True):
    """
    Fetches a file from Google Cloud Storage bucket.

    :param bucket_name: Name of the GCS bucket.
    :param file_path: Path of the file within the bucket.
    :param as_text: Whether to return the content as text (True) or binary (False).
    :return: Contents of the file as a string or binary depending on `as_text`.
    """
    try:
        # Initialize the GCS client
        client = get_gcs_client()

        # Reference the GCS bucket
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(file_path)

        # Check if the file (blob) exists
        if not blob.exists():
            raise FileNotFoundError(f"File {file_path} not found in bucket {bucket_name}")

        # Download the file content as text or binary
        if as_text:
            return blob.download_as_text()
        else:
            return blob.download_as_bytes()  # For binary files like images

    except Exception as e:
        raise RuntimeError(f"An error occurred while fetching the file from GCS: {str(e)}")
