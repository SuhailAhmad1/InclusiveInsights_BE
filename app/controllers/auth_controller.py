from datetime import timedelta
from sqlalchemy.exc import SQLAlchemyError
from starlette.responses import JSONResponse

from app.crud.user_crud import get_user_by_email_db, create_new_user_db, update_login_time_db
from app.core.utils import response_json
from app.services.auth_service import AuthService
from app.core.logger import logger
from config import ACCESS_TOKEN_EXPIRE_DAYS, REFRESH_TOKEN_EXPIRE_DAYS, USER_SIGNUP_KEY

auth_service = AuthService()


def register_user_controller(user):
    """
        Controller to register user000
        :param user: user details
        :return: response
    """
    try:
        logger.debug(str("Checking for secret_key") +
                     '[BE_Arcolab_new/app/controllers/auth_controller.py:10]')

        if user.secret_key != USER_SIGNUP_KEY:
            return response_json({}, "Mention the secret key", 400)

        logger.debug(str(f"{user.email} is trying to signup...") +
                     '[register_user] [/app/controllers/auth_controller.py:20]')

        userDetails = get_user_by_email_db(user.email)

        if not userDetails:
            create_new_user_db(user)
            logger.debug(str("User created successfully...") +
                         '[BE_Arcolab_new/app/controllers/auth_controller.py:27]')

            return response_json({}, "Account created successfully.", 201)

        return response_json({}, "User already exists", 409)

    except SQLAlchemyError as e:
        return response_json({}, "Database error", 500)

    except Exception as e:
        logger.exception(str(e) +
                         '[BE_Arcolab_new/app/controllers/auth_controller.py:37]')
        return response_json({}, 'Something went wrong', 500)


def login_user_controller(user):
    """
        Controller to login user
        :param user: user details
        :return: Success Message and tokens in response headers
    """
    try:
        logger.debug(str(f"{user.email} is trying to log in...") +
                     '[BE_Arcolab_new/app/controllers/auth_controller.py:49]')
        userDetails = get_user_by_email_db(user.email)

        if userDetails and auth_service.verify_password(user.password, userDetails['password']):
            logger.debug(str("Creating access token...") +
                         '[BE_Arcolab_new/app/controllers/auth_controller.py:55]')

            access_token_expires = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
            access_token = auth_service.create_access_token(
                data={"sub": userDetails['email']}, expires_delta=access_token_expires
            )

            refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
            refresh_token = auth_service.create_access_token(
                data={"sub": userDetails['email']}, expires_delta=refresh_token_expires
            )

            update_login_time_db(userDetails['id'])

            response_headers = {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "Access-Control-Expose-Headers": 'access_token, refresh_token'
            }

            data = {
                "data": {},
                "message": "Login Successful"
            }

            logger.debug(str("Login Successfull...") +
                         '[BE_Arcolab_new/app/controllers/auth_controller.py:83]')

            return JSONResponse(content=data, headers=response_headers, status_code=200)

        logger.warning(str("User does not exist...") +
                       '[BE_Arcolab_new/app/controllers/auth_controller.py:89]')
        return response_json({}, "Invalid credentials", 401)

    except SQLAlchemyError as e:
        return response_json({}, "Database error", 500)

    except Exception as e:
        logger.exception(str(e) +
                         '[BE_Arcolab_new/app/controllers/auth_controller.py:90]')
        return response_json({}, 'Something went wrong', 500)


def refresh_access_token_controller(current_user):
    """
        Controller to get refresh access token
        :param current_user: current user details taken from refresh_token
        :return: access_token as response
    """
    try:
        username = current_user.get("email")
        logger.debug(str(f"{username} is trying to get refresh token...") +
                     '[BE_Arcolab_new/app/controllers/auth_controller.py:107]')

        if username is None:
            logger.error(str("Invalid token...") +
                         '[BE_Arcolab_new/app/controllers/auth_controller.py:111]')
            return response_json({}, "Invalid token", 400)

        access_token_expires = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
        new_access_token = auth_service.create_access_token(
            data={"sub": username}, expires_delta=access_token_expires
        )

        logger.debug(str("Successfully generated a new token...") +
                     '[BE_Arcolab_new/app/controllers/auth_controller.py:120]')

        return {"access_token": new_access_token}

    except SQLAlchemyError as e:
        return response_json({}, "Database error", 500)

    except Exception as e:
        logger.exception(str(e) +
                         '[BE_Arcolab_new/app/controllers/auth_controller.py:126]')
        return response_json({}, "Something Went wrong", 500)


def get_user_info_controller(current_user):
    """
        Controller to get user info
        :param current_user: current user details
        :return: user details as response
    """
    try:
        username = current_user.get("email")
        logger.debug(str(f'{username} is asking for his info...') +
                     '[BE_Arcolab_new/app/controllers/auth_controller.py:149]')

        if username is None:
            return response_json({}, "Invalid token", 400)

        user_details = {
            "username": current_user["name"],
            "email": current_user["email"],
            "role": current_user["role"]
        }
        logger.debug(str("Successfully recieved the user info...") +
                     '[BE_Arcolab_new/app/controllers/auth_controller.py:160]')
        return response_json(user_details, "User info fetched successfully", 200)

    except SQLAlchemyError as e:
        return response_json({}, "Database error", 500)

    except Exception as e:
        logger.exception(str(e) +
                         '[BE_Arcolab_new/app/controllers/auth_controller.py:168]')
        return response_json({}, "Something Went wrong", 500)
