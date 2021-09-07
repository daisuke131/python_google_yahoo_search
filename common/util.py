import os
from datetime import datetime

from dotenv import load_dotenv


def hyphen_now():
    return datetime.now().strftime("%Y-%m-%d-%H-%M-%S")


def time_now():
    return datetime.now().strftime("%Y/%m/%d %H:%M:%S")


def filename_creation(filename: str) -> str:
    return "{filename}_{datetime}".format(filename=filename, datetime=hyphen_now())


def fetch_env(env_key: str) -> str:
    load_dotenv()
    return os.getenv(env_key)


def fetch_absolute_path(folder_name: str) -> str:
    return os.path.join(os.getcwd(), folder_name)
