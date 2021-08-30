import os

# import re
from pathlib import Path
from time import sleep

from common.driver import Driver
from common.ggl_spreadsheet import Gspread
from common.util import hyphen_now

SS_FOLDER_PATH = os.path.join(os.getcwd(), "screenshot")
dir = Path(SS_FOLDER_PATH)
dir.mkdir(parents=True, exist_ok=True)


class Scraping:
    def __init__(self, search_word: str) -> None:
        self.g_drive = Gspread()
        self.search_query: str = self.fetch_query(search_word)
        self.google_url: str = self.fetch_google_url()
        self.yahoo_url: str = self.fetch_yahoo_url()
        self.google_datas: list = []
        self.yahoo_datas: list = []

    def fetch_query(self, search_word: str) -> str:
        search_words: list = search_word.split()
        search_query = "+".join(search_words)
        self.search_word_title = search_query
        return search_query

    def fetch_google_url(self) -> str:
        self.url: str = "https://www.google.com/search?q=" + self.search_query
        return self.url

    def fetch_yahoo_url(self) -> str:
        self.url: str = "https://search.yahoo.co.jp/search?p=" + self.search_query
        return self.url

    def scraping(self) -> None:
        driver = Driver()
        self.g_drive.create_folder(self.search_query + "_" + hyphen_now())
        self.fetch_google_data(driver)
        self.fetch_yahoo_data(driver)
        driver.quit()

    def fetch_google_data(self, driver):
        driver.get(self.google_url)
        sleep(2)
        ads = driver.els_selector(".qGXjvb")
        for el in ads:
            # el.find_element_by_css_selector("div > span").text
            self.google_datas.append(el.text)
        # self.google_datas = dict(zip(key, val))
        self.fetch_img(driver, "google")

    def fetch_yahoo_data(self, driver):
        driver.get(self.yahoo_url)
        sleep(2)
        ads = driver.els_selector(".sw-Card.Ad.js-Ad")
        for el in ads:
            # el.find_element_by_css_selector("h3").text
            self.yahoo_datas.append(el.text)
        # self.yahoo_datas = dict(zip(key, val))
        self.fetch_img(driver, "yahoo")

    def fetch_img(self, driver, search_kind: str):
        # スクショして一時的にローカルフォルダに保存
        driver.save_screenshot(SS_FOLDER_PATH, f"{search_kind}.png")
        # ローカル保存した画像をgoogleドライブに保存
        self.g_drive.save_file(SS_FOLDER_PATH, f"{search_kind}.png")
        # ローカル画像ファイル削除
        os.remove(SS_FOLDER_PATH + "/" + f"{search_kind}.png")

    def write_spread_sheet(self):
        self.g_drive.create_spreadsheet("data")
        self.g_drive.append_row(["google検索"])
        for val in self.google_datas:
            self.g_drive.append_row([val])
        self.g_drive.append_row(["yahoo検索"])
        for val in self.yahoo_datas:
            self.g_drive.append_row([val])


def scraping():
    my_scraping = Scraping("amazon フィギュア棚")
    # スクレイピング+グーグルドライブに保存
    my_scraping.scraping()
    my_scraping.write_spread_sheet()


scraping()
