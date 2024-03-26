from datetime import timedelta, datetime, timezone
from jose import jwt, JWTError
from os import getenv
from passlib.context import CryptContext
from ..db import userCollection
from ..schema import userEntity
from fastapi import HTTPException, status, Depends,Request
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from ..modal import TokenData

# context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Schema for token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/user/token")


async def verify_password(password: str, hash_password: str):
    return pwd_context.verify(password, hash_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def get_user_by_username(username: str):
    return userEntity(userCollection.find_one({"username": username}))


def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()

    if expires_delta:
        expire: datetime = datetime.now(timezone.utc) + expires_delta

    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    to_encode.update({"exp": expire})

    # encode jwt token;
    encoded_token = jwt.encode(
        to_encode, key=getenv("SECRET_KEY"), algorithm=getenv("ALGORITHM")
    )
    return encoded_token


async def authenticate_user(username: str, password: str):
    user = userCollection.find_one({"username": username})

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username.",
        )

    user = userEntity(user)
    # verify password
    password_verify = await verify_password(password, user.get("password"))

    if not password_verify:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password.",
        )
    user.pop("password")
    return user


# async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
#     print("start")
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, getenv("SECRET_KEY"), algorithms=[getenv("ALGORITHM")])
#         # print(payload)
#         token_data = TokenData(**payload)
#     except JWTError:
#         raise credentials_exception
#     user =await get_user_by_username(token_data.username)
#     print(user)
#     if not user:
#         raise credentials_exception
#     return user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)],request:Request):
    print("start")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, getenv("SECRET_KEY"), algorithms=[getenv("ALGORITHM")]
        )
        # print(payload)
        token_data = TokenData(**payload)
    except JWTError:
        raise credentials_exception
    user = await get_user_by_username(token_data.username)
    print(user)
    if not user:
        raise credentials_exception
    request.state.user=user
    return user
