from datetime import datetime
from bson import ObjectId
from app.crud.crud_utils import hash_password


async def get_user_by_email_db(email, db):
    """
        Function to get user details by email from db
        :param email: email of the user
        :return: userDetails
    """
    try:
        user = await db.users.find_one({'email': email})
        return {
            "id": str(user["_id"]),
            "name": user["name"],
            "email": user["email"],
            "password": user["password"],
            "user_role": user["user_role"]
        } if user else {}

    except Exception as e:
        raise e


async def create_new_user_db(user, db):
    """
        Function to create new user in the db
        :param user: user details
        :return: status
    """
    try:
        data = {
            "email": user.email,
            "name": user.name,
            "password": hash_password(user.password),
            "user_role": user.user_role,
            "last_login_time": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        result = await db.users.insert_one(data)
        if result.acknowledged:
            return True
        return False

    except Exception as e:
        raise e


async def update_login_time_db(user_id, db):
    """
        Function to update login and logout time in the db
        :param user_id: user_id
    """
    try:
        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"last_login_at": datetime.now()}}
        )

    except Exception as e:
        raise e
