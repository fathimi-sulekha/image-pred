import hashlib

def generate_cache_key(file_content: bytes) -> str:
    """Generate a unique cache key for an image file."""
    return hashlib.md5(file_content).hexdigest()
