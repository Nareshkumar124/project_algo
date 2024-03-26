from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from ..modal import Token
from datetime import timedelta
from os import getenv
from ..auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_password_hash,
)
from ..modal import UserDb, User,TokenData
from ..db import userCollection


router = APIRouter(prefix="/user", tags=["user"])


@router.post("/register", response_model=User, response_model_exclude={"password"})
async def register_user(user: User) -> User:
    user.password = get_password_hash(user.password)
    print(user.password)
    print(user)
    user_in_db = userCollection.insert_one(user.model_dump())
    print(user_in_db)
    if not user_in_db:
        raise HTTPException(status_code=500, detail="Internal server error")
    return user


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    user = await authenticate_user(form_data.username, form_data.password)
    access_token_expires = timedelta(minutes=int(getenv("ACCESS_TOKEN_EXPIRE_MINUTES")))
    access_token = create_access_token(data=user, expires_delta=access_token_expires)
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=TokenData)
async def get_user(user: Annotated[dict, Depends(get_current_user)]):
    print(TokenData(**user))
    return user
