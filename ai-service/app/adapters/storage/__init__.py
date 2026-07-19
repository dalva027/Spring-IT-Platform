from app.adapters.storage.local import PostgresStorage

_storage: PostgresStorage | None = None


def get_storage() -> PostgresStorage:
    """Process-wide storage adapter (swap for a DynamoDB impl on AWS)."""
    global _storage
    if _storage is None:
        _storage = PostgresStorage()
    return _storage
