import io
from typing import List

import googleapiclient
from fastapi import UploadFile, APIRouter, File, HTTPException, Depends
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseUpload
from starlette.responses import StreamingResponse

from app.database import get_db_spatial_ai
from app.google_drive import drive_service, get_google_drive
from app.schemas.google_drive import FileUploadResponse, FileDetail, DeleteResponse

router = APIRouter()


@router.post("/fileUpload", response_model=FileUploadResponse)
async def upload_file_to_drive(file: UploadFile = File(...), drive_service=Depends(get_google_drive)):
    try:
        file_metadata = {'name': file.filename}

        # Read the file and wrap it in MediaIoBaseUpload
        media = MediaIoBaseUpload(io.BytesIO(await file.read()), mimetype=file.content_type)

        # Upload the file to Google Drive
        uploaded_file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name'
        ).execute()

        # Construct the file URL
        file_url = f"https://drive.google.com/file/d/{uploaded_file.get('id')}/view"

        return {
            "fileId": uploaded_file.get("id"),
            "fileName": uploaded_file.get("name"),
            "fileURL": file_url
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unable to upload file to Google Drive: {str(e)}")

@router.get("/listFiles", response_model=List[FileDetail])
async def list_files(drive_service=Depends(get_google_drive)):
    try:
        # List the first 10 files from Google Drive
        results = drive_service.files().list(
            pageSize=10,
            fields="nextPageToken, files(id, name)"
        ).execute()

        files = results.get('files', [])

        # Prepare the response structure
        file_details = [
            FileDetail(id=file.get('id'), name=file.get('name'))
            for file in files
        ]

        return file_details

    except HttpError as e:
        raise HTTPException(status_code=500, detail=f"Unable to retrieve files from Google Drive: {str(e)}")


@router.get("/downloadFile/{id}")
async def download_file(id: str, drive_service=Depends(get_google_drive)):
    try:
        # Retrieve the file from Google Drive using its file ID
        request = drive_service.files().get_media(fileId=id)
        file_stream = io.BytesIO()

        # Download the file content
        downloader = googleapiclient.http.MediaIoBaseDownload(file_stream, request)

        done = False
        while not done:
            status, done = downloader.next_chunk()

        # Seek to the beginning of the stream after downloading
        file_stream.seek(0)

        headers = {
            "Content-Disposition": f"attachment; filename={id}",
            "Content-Type": "application/octet-stream",
        }

        return StreamingResponse(file_stream, headers=headers)

    except HttpError as e:
        raise HTTPException(status_code=500, detail=f"Unable to retrieve file from Google Drive: {str(e)}")


@router.delete("/deleteFile/{id}", response_model=DeleteResponse)
async def delete_file(id: str, db=Depends(get_db_spatial_ai), drive_service=Depends(get_google_drive)):
    try:
        # Delete the file from Google Drive
        drive_service.files().delete(fileId=id).execute()

        # Prepare the response message
        response = {"message": f"File with ID {id} has been deleted"}

        # Update the MongoDB collection
        filter_query = {"documentationLinks.fileId": id}
        update_query = {"$pull": {"documentationLinks": {"fileId": id}}}
        collection = db.get_collection("Company")
        update_result = await collection.update_one(filter_query, update_query)

        if update_result.modified_count == 0:
            raise HTTPException(status_code=500, detail="File ID not found in MongoDB or no update performed")

        return response

    except HttpError as e:
        raise HTTPException(status_code=500, detail=f"Unable to delete file from Google Drive: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unable to update MongoDB collection: {str(e)}")
