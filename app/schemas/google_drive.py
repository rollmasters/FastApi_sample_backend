from pydantic import BaseModel


class FileUploadResponse(BaseModel):
    fileId: str
    fileName: str
    fileURL: str

class FileDetail(BaseModel):
    id: str
    name: str

class DeleteResponse(BaseModel):
    message: str