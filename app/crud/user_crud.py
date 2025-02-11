from sqlalchemy import text
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

from app.core.logger import logger
from app.core.db import engine as db
from app.crud.crud_utils import hash_password


def get_user_by_email_db(email):
    """
        Function to get user details by email from db
        :param email: email of the user
        :return: userDetails
    """
    try:
        with db.connect() as conn:
            query = text("""
                        SELECT 
                        id, name, email, password, role
                        FROM user
                        WHERE email = :email
                        """)
            result = conn.execute(query,
                                  {"email": email}
                                  )
            userDetails = result.fetchone()
            if userDetails:
                column_names = result.keys()
                userDetails = dict(zip(column_names, userDetails))
                return userDetails
            else:
                return {}

    except SQLAlchemyError as e:
        logger.exception(str(e) +
                         '[BE_Arcolab_new/app/crud/user_crud.py:34]')
        raise e

    except Exception as e:
        logger.exception(str(e) +
                     '[BE_Arcolab_new/app/crud/user_crud.py:38]')
        raise e


def create_new_user_db(user):
    """
        Function to create new user in the db
        :param user: user details
        :return: status
    """
    try:
        with db.connect() as conn:
            query = text("""
                        INSERT INTO user(name, email, password, role) 
                        VALUES (:name, :email, :password, :user_role)
                        """)
            conn.execute(query,
                         {
                            "email": user.email,
                            "name": user.name, 
                            "password": hash_password(user.password), 
                            "user_role": user.user_role}
                         )

            conn.commit()
            return True

    except SQLAlchemyError as e:
        logger.exception(str(e) +
                         '[BE_Arcolab_new/app/crud/user_crud.py:64]')
        raise e

    except Exception as e:
        logger.exception(str(e) +
                     '[Workflow_BE/app/services/db_services.py:60]')
        raise e

def update_login_time_db(user_id):
    """
        Function to update login and logout time in the db
        :param user_id: user_id
    """
    try:
        with db.connect() as conn:
            query = text("""
                        UPDATE user
                        SET last_login = CURRENT_TIMESTAMP()
                        WHERE id = :user_id
                        """)

            conn.execute(query, {"user_id": user_id})

            conn.commit()

    except SQLAlchemyError as e:
        logger.exception(str(e)+
                         '[BE_Arcolab_new/app/crud/user_crud.py:101]')
        raise e
    
    except Exception as e:
        logger.exception(str(e)+
                     '[BE_Arcolab_new/app/crud/user_crud.py:106]')
        raise e