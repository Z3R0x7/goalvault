import bleach


def sanitize_text(text, max_length=5000):
    if not text:
        return text
    cleaned = bleach.clean(str(text), tags=[], strip=True)
    return cleaned[:max_length]
