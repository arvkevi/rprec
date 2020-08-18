import logging
import numpy as np
import pandas as pd
import spacy

from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import pairwise_distances

from rprec.db import (
    db_connection,
    query_articles,
    write_similarities_to_database,
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


def tagged_docs_to_vectors(model, tagged_docs):
    """Make vectors suitable for downstream ML tasks"""
    sents = tagged_docs
    regressors = [
            model.infer_vector(document.words, steps=20)
            for document in sents
        ]
    return np.array(regressors)


def run_recommender(
    database_name,
    database_user,
    database_password,
    database_server,
    database_port,
    database_url,
    top_five=True,
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
    :param top_five: If True, only record the top five most similar articles frr each scoring type.
    :type top_five: bool
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
    # doc2vec
    tagged_docs = [
        TaggedDocument(doc, [label]) for doc, label in zip(processed_texts, labels)
    ]
    model = Doc2Vec(vector_size=100, min_count=2, epochs=50)
    model.build_vocab(tagged_docs)
    logger.info("Training doc2vec model...")
    model.train(tagged_docs, total_examples=model.corpus_count, epochs=model.epochs)
    doc_vectors = tagged_docs_to_vectors(model, tagged_docs)

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
        if i % 10 == 0:
            logger.info(f"Finished recording {i} articles")
        slug = labels[i]
        if top_five:
            top_5_indices = cosine_similarities[i].argsort()[:-7:-1][1:]
            similar_slugs = [labels[i] for i in top_5_indices]
            cosine_scores = [cosine_similarities[i][j] for j in top_5_indices]
            d2v_similar_results = model.docvecs.most_similar([doc_vectors[i, :]], topn=6)[1:]
            d2v_similar_slugs, d2v_scores = zip(*d2v_similar_results)
        else:
            similar_slugs = labels
            cosine_scores = cosine_similarities[i]
            d2v_similar_results = model.docvecs.most_similar([doc_vectors[i, :]], topn=len(processed_texts))
            d2v_similar_slugs, d2v_scores = zip(*d2v_similar_results)
        
        cosinedf = pd.DataFrame({
            'slug': [slug] * len(similar_slugs),
            'similar_slug': similar_slugs,
            'cosine_scores': cosine_scores
        })
        d2vdf = pd.DataFrame({
            'similar_slug': d2v_similar_slugs,
            'd2v_scores': d2v_scores
            })
        results.extend(cosinedf.merge(d2vdf, on='similar_slug', how='outer').dropna(subset=['slug', 'similar_slug']).to_numpy().tolist())

    write_similarities_to_database(results, connection)
