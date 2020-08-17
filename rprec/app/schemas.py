from typing import Dict, List, Optional

from pydantic import BaseModel


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
