import os

from redis import Redis
from redis.retry import Retry
from redis.backoff import ExponentialBackoff
from redis.exceptions import ConnectionError, TimeoutError


def get_redis_connection():
    """
    Builds and returns a new Redis connection.
    Called separately by app.py and worker.py since each
    runs in its own process and needs its own live connection.
    """
    redis_url = os.getenv("REDIS_URL")

    if not redis_url:
        raise ValueError("REDIS_URL is not set in environment or .env file.")

    return Redis.from_url(
        redis_url,
        health_check_interval=15,
        socket_keepalive=True,
        socket_timeout=10,
        retry_on_timeout=True,
        retry_on_error=[ConnectionError, TimeoutError],
        retry=Retry(ExponentialBackoff(cap=10, base=1), 3),
    )