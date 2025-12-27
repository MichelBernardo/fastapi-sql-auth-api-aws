from typing import Optional, List
from pydantic import BaseModel, EmailStr

from schemas.article_schema import ArticleSchema


class UserSchemaBase(BaseModel):
    id: Optional[int] = None
    name: str
    last_name: str
    email: EmailStr
    password: str
    is_admin: bool = False
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True


class UserSchemaCreate(UserSchemaBase):
    password: str


class UserSchemaArticles(UserSchemaBase):
    articles: Optional[List[ArticleSchema]]


class UserSchemaUp(UserSchemaBase):
    name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_admin: Optional[bool] = None
    avatar_url: Optional[str] = None