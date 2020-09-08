import logging
import os
import sys

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)
logging.basicConfig(level="INFO")

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
    logger.critical(
        "The DATABASE_URL environment variable is not set. Please set it to a valid database url."
    )
    sys.exit(1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
