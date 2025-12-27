from typing import List, Optional, Any

from fastapi import APIRouter, status, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from fastapi import UploadFile, File

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models.__all_models import UserModel
from schemas.user_schema import UserSchemaBase, UserSchemaCreate, UserSchemaArticles, UserSchemaUp
from schemas.user_mapper import user_to_schema, user_to_articles_schema
from core.deps import get_current_user, get_session
from core.security import generate_password_hash
from core.auth import authenticate, create_token_access
from services.s3_service import upload_avatar_to_s3, generate_presigned_url


router = APIRouter()


# GET logged
@router.get('/logged', response_model=UserSchemaBase)
async def get_logged(logged_user: UserModel = Depends(get_current_user)):
    return user_to_schema(logged_user)


# POST / Sign up
@router.post('/signup', status_code=status.HTTP_201_CREATED, response_model=UserSchemaBase)
async def post_user(user: UserSchemaCreate, db: AsyncSession = Depends(get_session)):
    new_user: UserModel = UserModel(
        name=user.name,
        last_name=user.last_name,
        email=user.email,
        password=generate_password_hash(user.password),
        is_admin=user.is_admin
    )

    async with db as session:
        session.add(new_user)
        await session.commit()

        return new_user


# GET users
@router.get('/', response_model=List[UserSchemaBase], status_code=status.HTTP_200_OK)
async def get_users(db: AsyncSession = Depends(get_session)):
    async with db as session:
        query = select(UserModel)
        result = await session.execute(query)
        users: List[UserSchemaBase] = result.scalars().unique().all()

        return users


# GET user
@router.get('/{user_id}', response_model=UserSchemaArticles, status_code=status.HTTP_200_OK)
async def get_user(user_id: int, db: AsyncSession = Depends(get_session)):
    async with db as session:
        query = select(UserModel).filter(UserModel.id == user_id)
        result = await session.execute(query)
        user: UserSchemaArticles = result.scalars().unique().one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return user_to_articles_schema(user)


# PUT user
@router.put('/{user_id}', response_model=UserSchemaBase, status_code=status.HTTP_202_ACCEPTED)
async def put_user(
        user_id: int,
        user: UserSchemaUp,
        db: AsyncSession = Depends(get_session),
        logged_user: UserModel = Depends(get_current_user)
        ):
    async with db as session:
        if not logged_user.is_admin and logged_user.id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                                detail='You do not have permission to modify this user.')

        query = select(UserModel).filter(UserModel.id == user_id)
        result = await session.execute(query)
        user_put = result.scalars().unique().one_or_none()

        if user_put:
            if user.name:
                user_put.name = user.name
            if user.last_name:
                user_put.last_name = user.last_name
            if user.email:
                user_put.email = user.email
            if user.is_admin:
                if logged_user.is_admin:
                    user_put.is_admin = user.is_admin
                else:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                        detail='You do not have permission to make this user an admin.')
            if user.password:
                user_put.password = generate_password_hash(user.password)

            await session.commit()

            return user_put
        else:
            raise HTTPException(detail='User not found',
                                status_code=status.HTTP_404_NOT_FOUND)


# DELETE user
@router.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
        user_id: int,
        db: AsyncSession = Depends(get_session),
        logged_user: UserModel = Depends(get_current_user)
        ):
    async with db as session:
        if not logged_user.is_admin and logged_user.id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                                detail='You do not have permission to modify this user.')

        query = select(UserModel).filter(UserModel.id == user_id)
        result = await session.execute(query)
        user: UserSchemaArticles = result.scalars().unique().one_or_none()

        if user:
            await session.delete(user)
            await session.commit()
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        else:
            raise HTTPException(detail='User not found', status_code=status.HTTP_404_NOT_FOUND)


# POST loggin
@router.post('/login')
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_session)):
    user = await authenticate(email=form_data.username, password=form_data.password, db=db)

    if not user:
        raise HTTPException(detail='Invalid access informations.', status_code=status.HTTP_400_BAD_REQUEST)

    return JSONResponse(
                content={
                    'access_token': create_token_access(sub=user.id),
                    'token_type': 'bearer'
                },
                status_code=status.HTTP_200_OK
            )

@router.post('/{user_id}/avatar', status_code=status.HTTP_202_ACCEPTED)
async def upload_avatar(
        user_id: int,
        file: UploadFile =  File(...),
        db: AsyncSession = Depends(get_session),
        logged_user: UserModel = Depends(get_current_user)
        ):
    if logged_user.id != user_id and not logged_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to upload this avatar."
        )

    async with db as session:
        query = select(UserModel).filter(UserModel.id == user_id)
        result = await session.execute(query)
        user = result.scalars().unique().one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        avatar_key = upload_avatar_to_s3(file, logged_user.id)
        logged_user.avatar_key = avatar_key
        await db.commit()

        avatar_url = generate_presigned_url(avatar_key)

        return {
            "avatar_url": avatar_url
        }