import logging
import requests
import time

from bs4 import BeautifulSoup

from rprec.db import db_connection, query_database_slugs, write_article_to_database

logger = logging.getLogger(__name__)
logging.basicConfig(level="INFO")


def tutorial_categores_from_rp_sitemap(sitemap_url):
    """Scrapes a list of tutorial categories from the Real Python sitemap.
    
    :param sitemap_url: The url string for the Real Python sitemap xml.
    :type sitemap_url: str
    :return: A list Real Python tutorial categories
    :rtype: list
    """
    soup = BeautifulSoup(requests.get(sitemap_url).text, "lxml")

    categories = []
    for loc in soup.select("url > loc"):
        if "tutorials" in loc.text:
            categories.append(loc.text)

    all_url = "https://realpython.com/tutorials/all/"
    categories.remove(all_url)

    return categories


def extract_slugs(soup):
    """extract article slugs from /tutorials/* page
    
    :param soup: A beautifulsoup4 object
    :type soup: bs4.BeautifulSoup
    :yield: article slug
    :rtype: str
    """
    for div in soup.findAll("div", {"class": "card-body m-0 p-0 mt-2"}):
        link = div.find("a", href=True)
        yield link["href"].strip("/")


def process_slugs(slugs):
    """Creates a dictionary of slugs by type: (article, interview, courses)
    
    :param slugs: List of article slugs
    :type slugs: list
    :return: Dictionary of article slugs separated by category 
    :rtype: dict
    """
    slugs_by_type = {
        "articles": [],
        "courses": [],
        "interviews": [],
    }
    for slug in slugs:
        if slug.startswith("courses/"):
            slugs_by_type["courses"].append(slug[8:])
        elif slug.startswith("interview"):
            slugs_by_type["interviews"].append(slug)
        else:
            slugs_by_type["articles"].append(slug)

    return slugs_by_type


def scrape_article(slug):
    """Scrapes the article text body from a Real Python tutorial page.
    
    :param slug: Name of the article slug to 
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


def scrape_category_pages_for_slugs(categories, database_slugs):
    """Scrape each category page for article slugs. Some category pages are paginated.
    
    :param categories: List of categories to scrape
    :type categories: list
    :param database_slugs: List of slugs already in the database
    :type database_slugs: list
    :return: List of new RP articles to scrape
    :rtype: list
    """
    slugs = []
    current_page_number = 1
    for category_url in categories:
        logger.info(f"scraping: {category_url}")
        category_page_url = f"{category_url}"
        response = requests.get(category_page_url)
        soup = BeautifulSoup(response.content, "html.parser")
        is_paginated = soup.find_all("li", {"class": "page-item"})
        time.sleep(1)

        if not is_paginated:
            for slug in extract_slugs(soup):
                if slug in slugs or slug in database_slugs:
                    continue
                slugs.append(slug)
            # move to the next category
            continue

        while True:
            # on the page listing articles for this category
            category_page_url = f"{category_url}page/{current_page_number}"
            response = requests.get(category_page_url)
            soup = BeautifulSoup(response.content, "html.parser")

            # extract article slugs
            for slug in extract_slugs(soup):
                if slug in slugs or slug in database_slugs:
                    continue
                slugs.append(slug)

            # should we go on?
            if current_page_number > 1:
                try:
                    find_last_page = soup.find("li", {"class": "page-item disabled"})
                    # Search for hex c2bb character, indicating last page
                    # Note: on the first page c2ab will be disabled
                    if find_last_page.text == bytes.fromhex("c2bb").decode("utf-8"):
                        break
                except AttributeError:
                    # we're in the middle pages, keep scrolling
                    pass

            current_page_number += 1
            time.sleep(5)
    return slugs


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
    categories = tutorial_categores_from_rp_sitemap(rp_sitemap_url)

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
    slugs = scrape_category_pages_for_slugs(categories, database_slugs)

    slugs_by_type = process_slugs(slugs)

    if not slugs_by_type["articles"]:
        logging.info("Did not find any new Real Python articles")

    # iterate the new RP articles and write them to db
    for slug in slugs_by_type["articles"]:
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
