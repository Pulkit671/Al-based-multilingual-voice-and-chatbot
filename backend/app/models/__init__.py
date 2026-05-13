from datetime import datetime, timezone


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def serialize_document(document: dict | None) -> dict | None:
    if document is None:
        return None

    serialized = {}
    for key, value in document.items():
        if key == "_id":
            serialized["id"] = str(value)
        elif key in {"user_id", "chat_id"}:
            serialized[key] = str(value)
        else:
            serialized[key] = value
    return serialized
