#!/bin/bash

cd db

alembic revision --autogenerate -m "init"
alembic upgrade head

cd ..

gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000

