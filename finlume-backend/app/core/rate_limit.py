from slowapi import Limiter
from slowapi.util import get_remote_address

# Dedicated limiter instance to avoid circular imports dynamically scaling limits.
limiter = Limiter(key_func=get_remote_address)
