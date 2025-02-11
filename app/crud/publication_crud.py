from datetime import datetime, timezone
from app.core.db import db

submitted_publication = db["submitted_publication"]

def submit_publication_db(docx_path, img_path, first_name, last_name, email, submission_type, publication_title, author_bio):
    try:
        data = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "submission_type": submission_type,
            "publication_title": publication_title, 
            "author_bio": author_bio,
            "docx_path": docx_path,
            "image_path": img_path,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "is_deleted": 0
        }
        result = submitted_publication.insert_one(data)
        if result.acknowledged:
            return True
        return False
    
    except Exception as e:
        raise e