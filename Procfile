web: uvicorn rprec.app.main:app --host=0.0.0.0 --port=${PORT:-5000}
worker: python rprec/__main__.py recommender --scrape=True