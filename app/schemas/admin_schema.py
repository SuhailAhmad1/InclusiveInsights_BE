from typing import List
from pydantic import BaseModel

class PublishSubmission(BaseModel):
    submission_id: str
    content: str

class EditDoc(BaseModel):
    doc_id: int
    new_doc_name: str