web: gunicorn src.main:app --bind 0.0.0.0:$PORT --worker-class aiohttp.GunicornWebWorker
worker: python src/main.py