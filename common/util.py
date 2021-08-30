# import os
import random
from datetime import datetime

from dotenv import load_dotenv


def hyphen_now():
    return datetime.now().strftime("%Y-%m-%d-%H-%M-%S")


def fetch_user_agent() -> str:
    load_dotenv()
    user_agent = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        + "(KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 "
        + "(KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        + "(KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        + "(KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
    ]
    return user_agent[random.randrange(0, len(user_agent), 1)]


def filename_creation(filename: str) -> str:
    # os.path.join(os.getcwd(), "csv")
    return "{filename}_{datetime}".format(filename=filename, datetime=hyphen_now())
