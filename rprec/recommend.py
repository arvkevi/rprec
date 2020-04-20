import json
import logging
import pandas as pd
import spacy

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import pairwise_distances

from rprec.db import (
    db_connection,
    query_articles,
    write_cosine_similarities_to_database,
)

logger = logging.getLogger(__name__)
logging.basicConfig(level="INFO")


def process_articles(all_articles):
    """Process the scraped Real Python articles 
    :param all_articles: The articles object from query_articles
    :return: processed texts and the slug ids
    """
    df = pd.DataFrame(all_articles, columns=["slug", "text"])

    raw_texts = df["text"].tolist()
    processed_texts = spacy_tokenizer(raw_texts)

    return processed_texts, df["slug"].tolist()


def spacy_tokenizer(raw_texts):
    """
    tokenize the text with spacy and remove stopwords
    :param raw_texts: List of texts
    :return:
    """
    # use spacy to process the raw text into spcay documents
    try:
        nlp = spacy.load("en")
    except OSError:
        from spacy.cli import download

        download("en")
        nlp = spacy.load("en")

    texts = []
    for doc in nlp.pipe(raw_texts, n_threads=4, disable=["tagger", "parser", "ner"]):
        texts.append(
            [preprocess_token(token) for token in doc if is_token_allowed(token)]
        )
    return texts


def is_token_allowed(token):
    """
        Only allow valid tokens which are not stop words
        and punctuation symbols.
    """
    if not token or not token.string.strip() or token.is_stop or token.is_punct:
        return False
    return True


def preprocess_token(token):
    """Reduce token to its lowercase lemma form"""
    return token.lemma_.strip().lower()


def identity_tokenizer(text):
    """dummy tokenizer for TfidfVectorizer"""
    return text


def article_cosine_similarity(processed_texts):
    """Return pairwise similarity of document vectors by performing tfidf on article tokens.
    
    :param processed_texts: list of article tokens
    :type processed_texts: list
    :return: pariwise cosine similarity values for each article
    """
    tfidf = TfidfVectorizer(
        tokenizer=identity_tokenizer,
        lowercase=False,
        ngram_range=(1, 1),
        min_df=0.025,
        max_df=0.5,
    )
    vectors = tfidf.fit_transform(processed_texts)
    # convert to similarity using 1 minus distance
    return 1 - pairwise_distances(vectors, vectors, metric="cosine")


def run_recommender(
    database_name,
    database_user,
    database_password,
    database_server,
    database_port,
    database_url,
):
    """processes Real Python article text, computes cosine similarity and writes top 3 scores to the database.
    
    :param database_name: Name of the db
    :type database_name: str
    :param database_user: database username
    :type database_user: str
    :param database_password: password for the db
    :type database_password: str
    :param database_server: where the database is hosted
    :type database_server: str
    :param database_port: port for the db
    :type database_port: int
    :param database_url: the environment variable for the database url in heroku
    :type database_url: str
    """
    # first connection reads
    connection = db_connection(
        database_name,
        database_user,
        database_password,
        database_server,
        database_port,
        database_url,
    )
    all_articles = query_articles(connection)
    processed_texts, labels = process_articles(all_articles)
    cosine_similarities = article_cosine_similarity(processed_texts)

    # second connection for write
    connection = db_connection(
        database_name,
        database_user,
        database_password,
        database_server,
        database_port,
        database_url,
    )
    results = []
    for i in range(len(processed_texts)):
        slug = labels[i]
        top_5_indices = cosine_similarities[i].argsort()[:-7:-1][1:]
        top_5_labels = [labels[i] for i in top_5_indices]
        top_5_scores = [cosine_similarities[i][_] for _ in top_5_indices]
        results.extend(
            [
                (slug, labels, scores)
                for labels, scores in zip(top_5_labels, top_5_scores)
            ]
        )

    write_cosine_similarities_to_database(results, connection)
