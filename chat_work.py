import requests

from common.util import fetch_absolute_path, fetch_env

APIKEY = fetch_env("CHATWORK_APIKEY")
ROOMID = fetch_env("ROOM_ID")  # チャットルームURLの末尾
URL = "https://api.chatwork.com/v2"


def send_message(message: str) -> bool:
    try:
        url = URL + "/rooms/" + ROOMID + "/messages"
        headers = {"X-ChatWorkToken": APIKEY}
        params = {"body": message}
        requests.post(url, headers=headers, params=params)
        return True
    except Exception:
        return False


def send_img(message: str, img_folder: str, imag_name: str) -> bool:
    try:
        url = URL + "/rooms/" + ROOMID + "/files"
        img_bin = open(fetch_absolute_path(img_folder) + "/" + imag_name, "rb")
        headers = {"X-ChatWorkToken": APIKEY}
        files = {
            "file": (imag_name, img_bin, "image/png"),
            "message": message,
        }
        requests.post(url, headers=headers, files=files)
        return True
    except Exception:
        return False
