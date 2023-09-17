from redis import Redis
from redis.exceptions import ConnectionError
from os import getenv

from src.conf import *
import time

times = 0
while times <= 3:
    try:
        logging.info(f"Connection try number {times} to Redis database")
        redis_client = Redis(
            host=getenv("REDIS_HOST"),
            port=getenv("REDIS_PORT"),
            decode_responses=True,
            db=0

            # password=getenv("REDIS_PASSWORD"),
            # ssl=bool(getenv("REDIS_SSL"))
        )
        db_response = redis_client.ping()
        if db_response:
            logging.info("CONNECTION COMPLETED")
            break

        logging.warning(f"UNEXPECTED RESPONSE: {db_response}")

    except ConnectionError as e:
        logging.error(f"CONNECTION REFUSED: {e.args}")
    except Exception as e:
        logging.error(f"ERROR OCCURRED: {e.args}")
    finally:
        times += 1
        time.sleep(1)
