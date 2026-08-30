import os
from dotenv import load_dotenv
from redis import Redis
from rq import Worker

# Load environment variables from your .env file
load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")

if not REDIS_URL:
    raise ValueError("REDIS_URL is not set in environment or .env file.")

redis_conn = Redis.from_url(
    REDIS_URL,
    health_check_interval=30,
    socket_keepalive=True,
    socket_timeout=10,
)

if __name__ == "__main__":
    worker = Worker(['emails'], connection=redis_conn)
    worker.work()