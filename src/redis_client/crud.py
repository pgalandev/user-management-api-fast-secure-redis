import json
from time import time_ns
from conf import *
from .connection import redis_client
from redis.exceptions import ResponseError
from typing import Optional


def set_user(key: str, data: str):
    try:
        redis_client.set(name=key, value=data)
        logging.info(f"User: {data} set at {time_ns()}")
    except ResponseError as error:
        logging.error(error.args)
        raise error


def get_user(key: str):
    try:
        user = redis_client.get(name=key)
        if not user:
            logging.warning(f"User with id= {key} not found")
            return None
        return json.loads(user)
    except ResponseError as error:
        logging.error(error.args)
        raise error


def get_all_users(total_number: Optional[int]):
    try:
        keys = redis_client.keys()[:total_number + 1] if total_number else redis_client.keys()
        users = [json.loads(redis_client.get(name=key)) for key in keys]
        if not users or len(users) == 0:
            logging.warning(f"No users found")
            return None
    except ResponseError as error:
        logging.error(error.args)
        raise error
    else:
        return users


def delete_user(key: str):
    try:
        redis_client.delete(key)
        logging.info(f"User with id: {key} has been deleted at {time_ns()}")
    except ResponseError as error:
        logging.error(error.args)
        raise error
    else:
        return True


def delete_all_users():
    try:
        keys = redis_client.keys()
        for key in keys:
            redis_client.delete(key)

        if len(redis_client.keys()) != 0:
            raise ResponseError("Elements not deleted")

    except ResponseError as error:
        logging.error(error.args)
        raise error
    else:
        return True
