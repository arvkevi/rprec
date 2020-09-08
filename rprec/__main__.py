import fire
import json
import os
import sys
import time

from rprec.scrape import run_scraper
from rprec.recommend import run_recommender


def scraper(
    database_name=None,
    database_user=None,
    database_password=None,
    database_server=None,
    database_port=5432,
    database_url=None,
):
    if database_url is None:
        try:
            DATABASE_URL = os.environ["DATABASE_URL"]
        except KeyError:
            DATABASE_URL = database_url
    else:
        DATABASE_URL = database_url

    if (
        any([database_name, database_user, database_password, database_server])
        and DATABASE_URL is not None
    ):
        sys.stderr.write(
            "Please either provide explicit connection arguments or a DATABASE_URL (heroku)"
        )
        sys.exit(1)

    run_scraper(
        database_name=database_name,
        database_user=database_user,
        database_password=database_password,
        database_server=database_server,
        database_port=database_port,
        database_url=DATABASE_URL,
    )


def recommender(
    database_name=None,
    database_user=None,
    database_password=None,
    database_server=None,
    database_port=5432,
    scrape=True,
    top_five=True,
):
    try:
        DATABASE_URL = os.environ["DATABASE_URL"]
    except KeyError:
        DATABASE_URL = None

    if (
        any([database_name, database_user, database_password, database_server])
        and DATABASE_URL is not None
    ):
        sys.stderr.write(
            "Please either provide explicit connection arguments or a DATABASE_URL (heroku)"
        )
        sys.exit(1)

    if scrape is True:
        scraper(
            database_name=database_name,
            database_user=database_user,
            database_password=database_password,
            database_server=database_server,
            database_port=database_port,
            database_url=DATABASE_URL,
        )
    run_recommender(
        database_name=database_name,
        database_user=database_user,
        database_password=database_password,
        database_server=database_server,
        database_port=database_port,
        database_url=DATABASE_URL,
        top_five=top_five,
    )


def main():
    fire.Fire(
        {
            "scraper": scraper,
            "recommender": recommender,
        }
    )


if __name__ == "__main__":
    main()
