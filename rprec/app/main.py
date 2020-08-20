from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session

from . import queries, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/articles/", response_model=List[schemas.Article], response_model_include={"slug"})
def list_article_slugs(skip: int = 0, limit: int = 10000, db: Session = Depends(get_db)):
    articles = queries.list_articles(db, skip=skip, limit=limit)
    return articles


@app.get("/articles/{slug}", response_model=schemas.Article)
def article_info(slug: str, db: Session = Depends(get_db)):
    article = queries.get_article(db, slug=slug)
    if article is None:
        raise HTTPException(status_code=404, detail="Article slug not found")
    return article

@app.get("/articles/similar/cosine/{slug}/", response_model=List[schemas.SimilarArticle], response_model_include={"slug", "similar_slug", "cosine_similarity"})
def top_n_cosine_similarity(slug: str, db: Session = Depends(get_db), limit: Optional[int] = 3):
    article = queries.get_cosine(db, slug=slug, limit=limit)
    if article is None:
        raise HTTPException(status_code=404, detail="Article slug not found")
    return article

@app.get("/articles/similar/doc2vec/{slug}/", response_model=List[schemas.SimilarArticle], response_model_include={"slug", "similar_slug", "doc2vec_similarity"})
def top_n_doc2vec_similarity(slug: str, db: Session = Depends(get_db), limit: Optional[int] = 3):
    article = queries.get_doc2vec(db, slug=slug, limit=limit)
    if article is None:
        raise HTTPException(status_code=404, detail="Article slug not found")
    return article



