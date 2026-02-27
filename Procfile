web: daphne -b 0.0.0.0 -p $PORT perplex.asgi:application
worker: celery -A perplex worker --loglevel=info --concurrency=2
beat: celery -A perplex beat --loglevel=info
