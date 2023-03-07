from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from jose import JWTError, jwt

from objects.resp_schemas import TokenData


ID_TOKEN_SECRET_KEY = (
    "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7ed"
)
# TODO: Need to updated refresh secret key
REFRESH_TOKEN_SECRET_KEY = (
    "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7ed"
)

TAG_SPEICAL_KEY = 'special_key'
ID_TOKEN_SPECIAL_KEY = 'ID Token'
REFRESH_TOKEN_SPECIAL_KEY = 'REFRESH Token'

ALGORITHM = "HS256"
ID_TOKEN_EXPIRY_MINUTES = 1
REFRESH_TOKEN_EXPIRY_MINUTES = 120
HEADER_KEY = "user_id"
EXPIRY_KEY = "expiry"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S.%f"

oauth2_refresh_token_scheme = OAuth2PasswordBearer(tokenUrl="login/id_token")
oauth2_id_token_scheme = OAuth2PasswordBearer(tokenUrl="login")


def create_id_token(data: dict):
    """
    [summary]: creates id token based on the user id provided
    """
    to_encode = data.copy()
    expiry_time = datetime.utcnow() + timedelta(minutes=ID_TOKEN_EXPIRY_MINUTES)
    to_encode.update({"expiry": expiry_time.__str__(), TAG_SPEICAL_KEY: ID_TOKEN_SPECIAL_KEY})
    encoded_data = create_token(to_encode, ID_TOKEN_SECRET_KEY, ALGORITHM)

    return encoded_data


def create_refresh_token(data: dict):
    """
    [summary]: creates refresh token based on the user id provided
    """
    to_encode = data.copy()
    expiry_time = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRY_MINUTES)
    to_encode.update({"expiry": expiry_time.__str__(), TAG_SPEICAL_KEY: REFRESH_TOKEN_SPECIAL_KEY})
    encoded_data = create_token(to_encode, REFRESH_TOKEN_SECRET_KEY, ALGORITHM)

    return encoded_data


def create_token(data_to_encode, secret_key, algo):
    """
    [summary]: creates JWT token
    """
    return jwt.encode(data_to_encode, secret_key, algorithm=algo)


def verify_id_token(token: str, credentials_exception):
    """[summary]: validates given id token
    """

    try:
        payload = jwt.decode(token, ID_TOKEN_SECRET_KEY, algorithms=[ALGORITHM])

        token_data = verify_payload(payload, credentials_exception)
    except JWTError:
        raise credentials_exception

    return token_data


def verify_refresh_token(token: str = Depends(oauth2_refresh_token_scheme)):
    """
    [summary]: validates given refresh token
    """

    credentials_exception = get_basic_authentication_execption()

    try:
        payload = jwt.decode(token, REFRESH_TOKEN_SECRET_KEY, algorithms=[ALGORITHM])

        token_data = verify_payload(payload, credentials_exception, REFRESH_TOKEN_SPECIAL_KEY)
    except JWTError:
        raise credentials_exception

    return token_data


def verify_payload(payload, credentials_exception, special_key_to_compare=ID_TOKEN_SPECIAL_KEY):
    """
    [summary]: verfies validity of the JWT token (ID token and Refresh token) received after decoding the token
    """

    id: str = payload.get(HEADER_KEY)

    if not id:
        raise credentials_exception
    else:
        token_expiry = datetime.strptime(payload.get(EXPIRY_KEY), DATE_FORMAT)
        if token_expiry < datetime.utcnow():
            # TODO: Detail message should not be including the id token expired message as it may lead to give more info for attacker
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"id token expired",
                headers={"www-Authenticate": "Bearer"},
            )
        
        if payload.get(TAG_SPEICAL_KEY) != special_key_to_compare:
            raise HTTPException (
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token provided",
                headers={"www-Authenticate": "Bearer"},
            )

    token_data = TokenData(id=id)

    return token_data


def get_current_user(token: str = Depends(oauth2_id_token_scheme)):
    """[summary]: fetching current user details based on the provided access_token
    """
    credentials_exception = get_basic_authentication_execption()

    return verify_id_token(token, credentials_exception)


def get_basic_authentication_execption():
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Couldnot validate credentials",
        headers={"www-Authenticate": "Bearer"},
    )

    return credentials_exception
