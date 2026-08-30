try:
    from celery import Celery
except ImportError:
    Celery = None


celery_app = Celery("ai_finance_saas") if Celery else None
