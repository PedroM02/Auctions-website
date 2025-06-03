from celery import Celery

celery_app = Celery(
    "tasks",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0",
    include=["app.finalise_products"]
)

celery_app.conf.beat_schedule = {
    'check-expired-auctions-every-1-minute': {
        'task': 'app.finalise_products.run_finalize_auctions',
        'schedule': 60.0  # a cada 60 segundos
    },
}

celery_app.conf.timezone = 'UTC'