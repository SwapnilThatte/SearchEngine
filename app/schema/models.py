from pydantic import BaseModel

class FilePathRequest(BaseModel):
    filepath : str

class DirPathRequest(BaseModel):
    dirpath : str

class SearchRequest(BaseModel):
    query : str