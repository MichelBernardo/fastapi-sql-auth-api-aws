from typing import List
from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models.__all_models import ArticleModel, UserModel
from schemas.article_schema import ArticleSchema
from core.deps import get_session, get_current_user


router = APIRouter()


# POST Article
@router.post('/', status_code=status.HTTP_201_CREATED, response_model=ArticleSchema)
async def post_article(
    article: ArticleSchema,
    logged_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    new_article: ArticleModel = ArticleModel(
        title=article.title,
        description=article.description,
        url_font=str(article.url_font),
        user_id=logged_user.id
    )

    db.add(new_article)
    await db.commit()

    return new_article


# GET Articles
@router.get('/', status_code=status.HTTP_200_OK, response_model=List[ArticleSchema])
async def get_articles(db: AsyncSession = Depends(get_session)):
    async with db as session:
        query = select(ArticleModel)
        result = await session.execute(query)
        articles: List[ArticleModel] = result.scalars().unique().all()

        return articles


# GET Article
@router.get('/{article_id}', status_code=status.HTTP_200_OK, response_model=ArticleSchema)
async def get_article(article_id: int, db: AsyncSession = Depends(get_session)):
    async with db as session:
        query = select(ArticleModel).filter(ArticleModel.id == article_id)
        result = await session.execute(query)
        article: ArticleModel = result.scalars().unique().one_or_none()

        if article:
            return article
        else:
            raise HTTPException(detail='Article not found.',
                                status_code=status.HTTP_404_NOT_FOUND)


# PUT Article
@router.put('/{article_id}', status_code=status.HTTP_202_ACCEPTED, response_model=ArticleSchema)
async def put_article(article_id: int,
                      article: ArticleSchema,
                      db: AsyncSession = Depends(get_session),
                      logged_user: UserModel = Depends(get_current_user)):
    async with db as session:
        query = select(ArticleModel).filter(ArticleModel.id == article_id)
        result = await session.execute(query)
        article_put: ArticleModel = result.scalars().unique().one_or_none()

        if article_put:
            if article.title:
                article_put.title = article.title
            if article.description:
                article_put.description = article.description
            if article.url_font:
                article_put.url_font = article.url_font
            if article_put.user_id != logged_user.id:
                article_put.user_id = logged_user.id

            await session.commit()
            return article_put
        else:
            raise HTTPException(detail='Article not found.',
                                status_code=status.HTTP_404_NOT_FOUND)


# DELETE Article
@router.delete('/{article_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(
    article_id: int,
    db: AsyncSession = Depends(get_session),
    logged_user: UserModel = Depends(get_current_user)):
    async with db as session:
        query = select(ArticleModel).filter(ArticleModel.id == article_id).filter(ArticleModel.user_id == logged_user.id)
        result = await session.execute(query)
        article_delete: ArticleModel = result.scalars().unique().one_or_none()

        if article_delete:
            await session.delete(article_delete)
            await session.commit()

            return Response(status_code=status.HTTP_204_NO_CONTENT)
        else:
            raise HTTPException(detail='Article not found.',
                                status_code=status.HTTP_404_NOT_FOUND)