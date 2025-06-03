from datetime import datetime, timedelta
from app.core.db import db
import pytz
import json
from bson import ObjectId

submitted_publication = db["submitted_publication"]


def submit_publication_db(
        docx_path,
        img_path,
        img_description,
        first_name,
        last_name,
        email,
        submission_type,
        publication_title,
        author_bio
):
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
            "image_description": img_description,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "is_deleted": 0,
            "description": "",
            "is_published": 0,
            "is_rejected": 0
        }
        result = submitted_publication.insert_one(data)
        if result.acknowledged:
            return str(result.inserted_id)
        return None

    except Exception as e:
        raise e


ist_timezone = pytz.timezone("Asia/Kolkata")


def get_all_publications_admin_db(start_date, end_date, category):
    try:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

        query = {
            "created_at": {
                "$gte": start_date,
                "$lt": end_date + timedelta(days=1)
            },
            "is_deleted": 0
        }

        if category != "All":
            query["submission_type"] = category

        publications = submitted_publication.find(query).sort("_id", -1)
        res = []

        total_published = 0
        total_pending = 0
        total_rejected = 0

        for publication in publications:
            status = "Published" if publication["is_published"] else "Rejected" if publication["is_rejected"] else "Pending"

            if status == "Published":
                total_published += 1
            elif status == "Rejected":
                total_rejected += 1
            else:
                total_pending += 1

            this_publiaction = {
                "id": str(publication["_id"]),
                "title": publication["publication_title"].title(),
                "created_at": (publication["created_at"] + timedelta(hours=5, minutes=30)).strftime("%d-%b-%Y %-I:%M %p"),
                "author": f'{publication["first_name"]} {publication["last_name"]}',
                "email": publication["email"],
                "img": publication["image_path"],
                "description": publication["description"],
                "category": publication["submission_type"],
                "status": status
            }
            res.append(this_publiaction)
        return res, total_published, total_pending, total_rejected

    except Exception as e:
        raise e


def delete_submission_db(submission_id):
    try:
        submitted_publication.update_one(
            {"_id": ObjectId(submission_id)},
            {"$set": {"is_deleted": 1}}
        )

    except Exception as e:
        raise e


def reject_submission_db(submission_id):
    try:
        submitted_publication.update_one(
            {"_id": ObjectId(submission_id)},
            {"$set": {"is_published": 0, "is_rejected": 1}}
        )
        return get_submission_data_admin_db(submission_id)
    except Exception as e:
        raise e


def publish_submission_db(payload):
    try:
        submitted_publication.update_one(
            {"_id": ObjectId(payload.submission_id)},
            {"$set": {
                "is_published": 1,
                "is_rejected": 0,
                "description": payload.content,
                "updated_at": datetime.now()
            }}
        )
        return get_submission_data_admin_db(payload.submission_id)
    except Exception as e:
        raise e


def get_all_publications_db(filter_by, search_param, page_number, limit):
    try:
        skip = (page_number - 1) * 6
        query = {
            "is_deleted": 0,
            "is_published": 1
        }
        if filter_by:
            query["submission_type"] = filter_by

        if search_param:
            query["publication_title"] = {
                "$regex": search_param, "$options": "i"}

        publications_cursor = submitted_publication.find(
            query).sort("updated_at", -1).skip(skip).limit(limit+1)
        publications_list = list(publications_cursor)  # Convert to list once

        # Check if there is a next page
        has_next_page = len(publications_list) > limit

        # Trim the extra document
        publications = publications_list[:limit]

        res = []
        # Print the results
        for publication in publications:
            this_publiaction = {
                "id": str(publication["_id"]),
                "title": publication["publication_title"].title(),
                "created_at": (publication["updated_at"] + timedelta(hours=5, minutes=30)).strftime("%d-%b-%Y %-I:%M %p"),
                "author": f'{publication["first_name"]} {publication["last_name"]}',
                "img": publication["image_path"],
                "image_description": publication["image_description"],
                "description": publication["description"],
                "category": publication["submission_type"]
            }

            res.append(this_publiaction)

        return res, has_next_page

    except Exception as e:
        raise e


def get_submission_data_admin_db(submission_id):
    try:
        publication_data = submitted_publication.find_one(
            {"_id": ObjectId(submission_id), "is_deleted": 0})
        if publication_data:
            status = "Published" if publication_data[
                "is_published"] else "Rejected" if publication_data["is_rejected"] else "Pending"
            data = {
                "id": str(publication_data["_id"]),
                "title": publication_data["publication_title"].title(),
                "created_at": (publication_data["created_at"] + timedelta(hours=5, minutes=30)).strftime("%d-%b-%Y %-I:%M %p"),
                "author": (f'{publication_data["first_name"].strip()} {publication_data["last_name"].strip()}').title(),
                "img": publication_data["image_path"],
                "description": publication_data["description"],
                "category": publication_data["submission_type"],
                "status": status,
                "image_description": publication_data["image_description"],
                "email": publication_data["email"],
                "author_bio": publication_data["author_bio"],
                "docx_path": publication_data["docx_path"]
            }
            return data
        return publication_data
    except Exception as e:
        raise e


def get_publication_data_db(publication_id):
    try:
        publication_data = submitted_publication.find_one(
            {"_id": ObjectId(publication_id), "is_deleted": 0, "is_published": 1})
        if publication_data:
            data = {
                "id": str(publication_data["_id"]),
                "title": publication_data["publication_title"].title(),
                "created_at": (publication_data["updated_at"] + timedelta(hours=5, minutes=30)).strftime("%d-%b-%Y %-I:%M %p"),
                "author": (f'{publication_data["first_name"].strip()} {publication_data["last_name"].strip()}').title(),
                "img": publication_data["image_path"],
                "description": publication_data["description"],
                "category": publication_data["submission_type"],
                "image_description": publication_data["image_description"],
            }
            return data
        return publication_data
    except Exception as e:
        raise e
