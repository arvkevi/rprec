from setuptools import find_packages, setup

from rprec import __project__, __version__

setup(
    name=__project__,
    packages=find_packages(),
    version=__version__,
    description="Recommend similar Real Python articles",
    author="Kevin Arvai",
    author_email="<arvkevi@gmail.com>",
    license="",
    entry_points={
        "console_scripts": [
            f"{__project__} = {__project__}.__main__:main",
        ]
    },
    install_requires=[
        "beautifulsoup4",
        "fire",
        "lxml",
        "pandas",
        "psycopg2-binary",
        "requests",
        "scikit-learn",
        "spacy",
    ],
)
