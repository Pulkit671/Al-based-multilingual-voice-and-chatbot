from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.database import Database

from app.database import get_database
from app.models import serialize_document, utc_now
from app.schemas.auth import (
    TokenResponse,
    UpdateLanguageRequest,
    UserLoginRequest,
    UserResponse,
    UserSignupRequest,
)
from app.utils.auth import create_access_token, get_current_user, hash_password, verify_password
from app.utils.translator import translator_service

router = APIRouter(prefix='/auth', tags=['Authentication'])


@router.post('/signup', response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def signup(payload: UserSignupRequest, db: Database = Depends(get_database)):
    if payload.password != payload.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Passwords do not match')

    existing_user = db.users.find_one({'email': payload.email.lower()})
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Email already registered')

    preferred_language = translator_service.normalize_language(payload.preferred_language)
    user_document = {
        'full_name': payload.full_name.strip(),
        'email': payload.email.lower(),
        'hashed_password': hash_password(payload.password),
        'preferred_language': preferred_language,
        'created_at': utc_now(),
    }
    result = db.users.insert_one(user_document)
    user = db.users.find_one({'_id': result.inserted_id})
    serialized_user = serialize_document(user)
    token = create_access_token(serialized_user['id'])
    return TokenResponse(access_token=token, user=UserResponse(**serialized_user))


@router.post('/login', response_model=TokenResponse)
def login(payload: UserLoginRequest, db: Database = Depends(get_database)):
    user = db.users.find_one({'email': payload.email.lower()})
    if not user or not verify_password(payload.password, user['hashed_password']):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid email or password')

    serialized_user = serialize_document(user)
    token = create_access_token(serialized_user['id'])
    return TokenResponse(access_token=token, user=UserResponse(**serialized_user))


@router.get('/me', response_model=UserResponse)
def me(current_user=Depends(get_current_user), db: Database = Depends(get_database)):
    user = db.users.find_one({'_id': ObjectId(current_user['id'])})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    return UserResponse(**serialize_document(user))


@router.put('/language', response_model=UserResponse)
def update_language(
    payload: UpdateLanguageRequest,
    current_user=Depends(get_current_user),
    db: Database = Depends(get_database),
):
    preferred_language = translator_service.normalize_language(payload.preferred_language)
    db.users.update_one(
        {'_id': ObjectId(current_user['id'])},
        {'$set': {'preferred_language': preferred_language}},
    )
    updated_user = db.users.find_one({'_id': ObjectId(current_user['id'])})
    return UserResponse(**serialize_document(updated_user))
