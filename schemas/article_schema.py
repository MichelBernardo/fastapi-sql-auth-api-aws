from typing import Optional
from pydantic import BaseModel, HttpUrl


class ArticleSchema(BaseModel):
    id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    url_font: Optional[HttpUrl] = None
    user_id: Optional[int] = None

    class Config:
        from_attributes = True