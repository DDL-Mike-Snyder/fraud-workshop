import os, hashlib, base64, uuid


def domino_short_id(length: int = 8) -> str:
    def short_fallback() -> str:
        return base64.urlsafe_b64encode(uuid.uuid4().bytes).decode("utf-8").rstrip("=")[:length]

    user    = os.environ.get("DOMINO_USER_NAME") or short_fallback()
    project = os.environ.get("DOMINO_PROJECT_ID")    or short_fallback()

    combined = f"{user}/{project}"
    digest   = hashlib.sha256(combined.encode()).digest()
    encoded  = base64.urlsafe_b64encode(digest).decode("utf-8").rstrip("=")
    return f"{user}_{encoded[:length]}"

