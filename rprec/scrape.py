import logging
import re
import requests
import time

from bs4 import BeautifulSoup

from rprec.db import db_connection, query_database_slugs, write_article_to_database

logger = logging.getLogger(__name__)
logging.basicConfig(level="INFO")


def tutorial_categories_from_rp_sitemap(sitemap_url, wrong_endpoints):
    """Scrapes a list of tutorial categories from the Real Python sitemap.
    
    :param sitemap_url: The url string for the Real Python sitemap xml.
    :type sitemap_url: str
    :param wrong_endpoints: endpoints that don't have content.
    :type wrong_endpoints: list
    :return: A list Real Python tutorial categories
    :rtype: list
    """
    soup = BeautifulSoup(requests.get(sitemap_url).text, "lxml")

    slugs_to_read = []
    for loc in soup.select("url > loc"):
        if any([f"https://realpython.com/{endpoint}" in loc.text for endpoint in wrong_endpoints]):
            continue
        else:
            slugs_to_read.append(loc.text)

    return slugs_to_read


def scrape_article(slug):
    """Scrapes the article text body from a Real Python tutorial page.
    
    :param slug: Name of the article slug to parse
    :type slug: str
    :return: (slug, author, article_text)
    :rtype: tuple
    """
    page_url = f"https://realpython.com/{slug}"
    response = requests.get(page_url)
    soup = BeautifulSoup(response.text, "html.parser")

    try:
        find_author = soup.find("a", href="#author")
        author = find_author.text
    except AttributeError:
        author = "Real Python"

    find_article_body = soup.find_all("div", {"class": "article-body"})

    article_text = ""
    for element in find_article_body:
        article_text += "\n" + "".join(element.findAll(text=True))

    return slug, author, article_text


def run_scraper(
    database_name,
    database_user,
    database_password,
    database_server,
    database_port,
    database_url,
):
    """Scrapes Real Python articles and writes new articles to a database.
    
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
    rp_sitemap_url = "http://realpython.com/sitemap.xml"

    wrong_endpoints = [
        'all',
        'quizzes',
        'questions',
        'resources',
        'security',
        'sponsorships',
        'start-here',
        'support',
        'team',
        'testimonials',
        'tutorials',
        'write-for-us',
        'learning-paths',
        'lessons',   
    ]
    urls_to_read = tutorial_categories_from_rp_sitemap(rp_sitemap_url, wrong_endpoints)

    # first check the database for slugs so we can skip those
    connection = db_connection(
        database_name,
        database_user,
        database_password,
        database_server,
        database_port,
        database_url,
    )
    database_slugs = query_database_slugs(connection)
    # slugs = scrape_category_pages_for_slugs(categories, database_slugs)


    # iterate the new RP articles and write them to db
    for url in urls_to_read:
        m = re.search(r'^.*\/([^/]*)/.*$', url)
        slug = m.group(1)
        if slug in database_slugs:
            continue
        article_object = scrape_article(slug)
        # I close the connection object after each write
        connection = db_connection(
            database_name,
            database_user,
            database_password,
            database_server,
            database_port,
            database_url,
        )
        write_article_to_database(article_object, connection)
        # be nice to RP
        time.sleep(1)
