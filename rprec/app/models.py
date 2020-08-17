from sqlalchemy import Column, Integer, String, Text, REAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey

from .database import Base


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(200), unique=True, index=True)
    author = Column('author', String(50))
    text = Column('text', Text)

    similar_articles = relationship("SimilarArticle", back_populates="query_article")


class SimilarArticle(Base):
    __tablename__ = "similar_articles"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(200), ForeignKey('articles.slug'), unique=True, index=True)
    similar_slug = Column(String(200), index=True)
    cosine_similarity = Column(REAL)
    doc2vec_similarity = Column(REAL)

    query_article = relationship("Article", back_populates="similar_articles")