from datetime import datetime, timedelta
from app.core.db import db
import pytz
import json
from bson import ObjectId

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
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "is_deleted": 0,
            "description": "Laws protecting the rights of disabled persons exist to ensure equal opportunities, accessibility, and non-discrimination in various aspects of life, including employment, education, and public services. These laws mandate that workplaces provide reasonable accommodations, such as modified workspaces or flexible schedules, so that individuals with disabilities can perform their job duties effectively. Similarly, educational institutions are required to implement inclusive policies, ensuring that students with disabilities receive necessary support, such as assistive technologies or personalized learning plans.\n\nPublic infrastructure and services must also be accessible to people with disabilities, with legal frameworks requiring ramps, elevators, and tactile paving in public spaces to enhance mobility. Transportation services, such as buses and trains, must provide accommodations like priority seating and audio-visual announcements. Digital accessibility has also become a legal priority, with websites and online platforms required to meet accessibility standards so that disabled individuals can access information and services without barriers.\n\nDisability rights laws often prohibit discrimination in healthcare and housing, ensuring that individuals receive fair treatment and reasonable modifications in medical facilities and residential settings. Governments enforce these laws through penalties and incentives, encouraging compliance among businesses and service providers. While significant progress has been made, advocacy groups continue to push for stronger enforcement and expanded rights to further improve the quality of life for disabled individuals and create a truly inclusive society."
        }
        result = submitted_publication.insert_one(data)
        if result.acknowledged:
            return True
        return False

    except Exception as e:
        raise e


ist_timezone = pytz.timezone("Asia/Kolkata")


def get_all_publications_db(filter_by, search_param, page_number, limit):
    try:
        skip = (page_number - 1) * 6
        query = {
            "deleted_at": None
        }
        if filter_by:
            query["submission_type"] = filter_by

        if search_param:
            query["publication_title"] = {
                "$regex": search_param, "$options": "i"}

        publications_cursor = submitted_publication.find(
            query).sort("_id", -1).skip(skip).limit(limit+1)
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
                "title": publication["publication_title"],
                "created_at": (publication["created_at"] + timedelta(hours=5, minutes=30)).strftime("%d-%b-%Y %-I:%M %p"),
                "author": f'{publication["first_name"]} {publication["last_name"]}',
                "img": publication["image_path"],
                "description": publication["description"],
                "category": publication["submission_type"]
            }

            res.append(this_publiaction)

        return res, has_next_page

    except Exception as e:
        raise e


def get_publication_data_db(publication_id):
    try:
        publication_data = submitted_publication.find_one(
            {"_id": ObjectId(publication_id)})
        if publication_data:
            data = {
                "id": str(publication_data["_id"]),
                "title": publication_data["publication_title"].title(),
                "created_at": (publication_data["created_at"] + timedelta(hours=5, minutes=30)).strftime("%d-%b-%Y %-I:%M %p"),
                "author": (f'{publication_data["first_name"].strip()} {publication_data["last_name"].strip()}').title(),
                "img": publication_data["image_path"],
                "description": publication_data["description"],
                "category": publication_data["submission_type"]
            }
            return data
        return publication_data
    except Exception as e:
        raise e
