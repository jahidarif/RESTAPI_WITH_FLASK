from dotenv import load_dotenv
from rq import Worker

from redis_conn import get_redis_connection

load_dotenv()

redis_conn = get_redis_connection()

if __name__ == "__main__":
    worker = Worker(["emails"], connection=redis_conn)
    worker.work()