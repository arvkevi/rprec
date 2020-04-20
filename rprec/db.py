import logging
import psycopg2
import sys

from psycopg2.extras import execute_values

logger = logging.getLogger(__name__)
logging.basicConfig(level="INFO")


def db_connection(
    database_name,
    database_user,
    database_password,
    database_server,
    database_port,
    database_url,
):
    """Connect to the database containing RP articles and similarity scores 
    
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
    :return: psycopg2 connection object
    :rtype: psycopg2 connection object
    """
    if database_url is not None:
        return psycopg2.connect(database_url, sslmode="allow")

    return psycopg2.connect(
        user=database_user,
        password=database_password,
        host=database_server,
        port=database_port,
        database=database_name,
    )


def query_database_slugs(connection):
    """Get the article slugs already in the database and return a list.
    
    :param connection: psycopg2 connection
    :type connection: psycopg2.extensions.connection
    :return: list of slugs in the database
    :rtype: list
    """
    try:
        cursor = connection.cursor()
        sql = """SELECT slug FROM articles"""
        cursor.execute(sql)
        slugs = [slug_[0] for slug_ in cursor.fetchall()]
    except psycopg2.Error as e:
        sys.stderr.write(f"Error while fetching data from PostgreSQL: {e}")
    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()

    return slugs


def query_articles(connection):
    """Query the Real Python articles from the db.

    :param connection: psycopg2 connection
    :type connection: psycopg2.extensions.connection
    :return: list of tuples as [(slug, text),]
    :rtype: list
    """
    try:
        cursor = connection.cursor()
        sql = """SELECT slug, text FROM articles"""
        cursor.execute(sql)
        articles = cursor.fetchall()
    except psycopg2.Error as e:
        sys.stderr.write("Error while fetching data from PostgreSQL", e)
    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()

    return articles


def write_article_to_database(article_object, connection):
    """write a new entry into the real python article text db.

    :param article_ojbect: dictionary with author and text fields
    :type article_object: dict
    :param connection: psycopg2 connection object
    :type connection: psycopg2 connection object
    """
    try:
        cursor = connection.cursor()
        sql = """INSERT INTO articles (slug, author, text) VALUES (%s, %s, %s);"""
        cursor.execute(sql, article_object)
        connection.commit()
        logger.info(f"wrote {article_object[0]} to the database")
    except psycopg2.Error as e:
        sys.stderr.write(f"Error while fetching data from PostgreSQL: {e}")
    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()


def write_cosine_similarities_to_database(results, connection):
    """record the new top 3 most similar articles by cosine similarity values

    :param results: list of tuples (slug, similar slug, cosine sim value)
    :type results: list
    :param connection: psycopg2 connection object
    :type connection: psycopg2 connection object
    """
    try:
        cursor = connection.cursor()
        sql_string = "INSERT INTO similar_articles (slug, similar_slug, cosine_similarity) VALUES %s;"
        execute_values(cursor, sql_string, results)
        # print(cursor.mogrify(sql_string, results).decode('utf8'))
        connection.commit()
        logger.info(f"recorded cosine_similarities to the database")
    except psycopg2.Error as e:
        sys.stderr.write(f"Error while fetching data from PostgreSQL: {e}")
    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()
