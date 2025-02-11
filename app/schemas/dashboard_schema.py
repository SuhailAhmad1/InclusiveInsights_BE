from typing import List
from pydantic import BaseModel

class DeleteDocs(BaseModel):
    doc_ids: List[int]

class EditDoc(BaseModel):
    doc_id: int
    new_doc_name: str