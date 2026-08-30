def run_scheduled_forecast() -> None:
    raise RuntimeError("Celery broker and forecasting artifact are not configured")


def scan_transaction_alerts() -> None:
    raise RuntimeError("Celery broker and transaction source are not configured")
