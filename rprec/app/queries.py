from sqlalchemy.orm import Session

from . import models


def get_article(db: Session, slug: str):
    return db.query(models.Article).filter(models.Article.slug == slug).first()


def list_articles(db: Session, skip: int = 0, limit: int = 10000):
    return db.query(models.Article).offset(skip).limit(limit).all()

def get_cosine(db: Session, slug: str, limit: int = 3):
    return db.query(models.SimilarArticle).filter(models.SimilarArticle.slug == slug).order_by(models.SimilarArticle.cosine_similarity.desc()).limit(limit + 1).all()[1:]

def get_doc2vec(db: Session, slug: str, limit: int = 3):
    return db.query(models.SimilarArticle).filter(models.SimilarArticle.slug == slug).order_by(models.SimilarArticle.doc2vec_similarity.desc()).limit(limit + 1).all()[1:]

