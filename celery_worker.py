from celery import Celery
import os

def make_celery():
    return Celery(
        "library_app",
        broker=os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0"),
        backend=os.getenv("CELERY_BACKEND_URL", "redis://redis:6379/0")
    )

celery = make_celery()