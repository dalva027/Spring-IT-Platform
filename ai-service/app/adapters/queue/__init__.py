from app.adapters.queue.local import DbJobQueue

_queue: DbJobQueue | None = None


def get_queue() -> DbJobQueue:
    """Process-wide queue adapter (swap for SQS on AWS)."""
    global _queue
    if _queue is None:
        _queue = DbJobQueue()
    return _queue
