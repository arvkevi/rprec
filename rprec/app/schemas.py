from math import isnan
from typing import List

from pydantic import BaseModel as PydanticBaseModel, validator


class BaseModel(PydanticBaseModel):
    @validator("*")
    def change_nan_to_none(cls, v, values, field):
        if field.outer_type_ is float and isnan(v):
            return None
        return v


class SimilarArticleBase(BaseModel):
    id: int


class SimilarArticle(SimilarArticleBase):
    similar_slug: str
    cosine_similarity: float
    doc2vec_similarity: float

    class Config:
        orm_mode = True


class ArticleBase(BaseModel):
    id: int


class Article(ArticleBase):
    slug: str
    author: str
    text: str
    similar_articles: List[SimilarArticle] = []

    class Config:
        orm_mode = True
