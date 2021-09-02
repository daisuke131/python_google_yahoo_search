import os
from pathlib import Path
from time import sleep

from common.driver import Driver
from common.ggl_spreadsheet import Gspread
from common.util import fetch_absolute_path, hyphen_now, time_now

SS_FOLDER_PATH = fetch_absolute_path("screenshot")
dir = Path(SS_FOLDER_PATH)
dir.mkdir(parents=True, exist_ok=True)


class Scraping:
    def __init__(self, search_word: str) -> None:
        self.g_drive = Gspread()
        self.search_query: str = self.fetch_query(search_word)
        self.google_url: str = self.fetch_google_url()
        self.yahoo_url: str = self.fetch_yahoo_url()
        self.google_store_ads: list = []
        self.google_ads: dict = {}
        self.google_sort_ads: list = []
        self.yahoo_ads: list = []
        self.nowdate = hyphen_now()  # 2021-09-10-00-00-00
        self.nowdatetime = time_now()  # 2021/09/10 00:00:00

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
        # self.g_drive.create_folder(self.search_query + "_" + hyphen_now())
        self.g_drive.create_folder(self.search_query.replace("+", "_"))
        self.fetch_google_data(driver)
        self.fetch_yahoo_data(driver)
        driver.quit()

    def fetch_google_data(self, driver):
        driver.get(self.google_url)
        sleep(2)
        driver.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # ads = driver.els_selector(".qGXjvb")
        # shop_ads = driver.els_selector(".mnr-c.pla-unit")
        # for ad in shop_ads:
        #     img_el = ad.find_element_by_css_selector("img")
        #     # img.find_element_by_css_selector(".pymv4e").text 名前
        #     # img.find_element_by_css_selector(".e10twf.T4OwTb").text　金額
        #     # img.find_element_by_css_selector(".LbUacb").text 店
        #     # if img.find_elements_by_css_selector(".cYBBsb") 送料無料
        #     self.google_store_ads.append(img_el.get_attribute("src"))

        # 日付追加
        self.google_ads["日付"] = self.nowdatetime
        self.google_ads["ランディングページ"] = driver.el_selector(".Zu0yb.LWAWHf.OSrXXb.qzEoUe")
        ads = driver.els_selector(".cUezCb.luh4tb.O9g5cc.uUPGi")
        for i in range(3):
            # タイトル
            if i == 0 or i == 1 or i == 2:
                try:
                    # self.google_ads.append(
                    #     ads[i].find_element_by_css_selector("div > span").text
                    # )
                    self.google_ads["広告タイトル" + str(i + 1)] = (
                        ads[i].find_element_by_css_selector("div > span").text
                    )
                except Exception:
                    self.google_ads["広告タイトル" + str(i + 1)] = ""
                    # self.google_ads.append("")
            # 説明文
            if i == 0 or i == 1:
                try:
                    # self.google_ads.append(
                    #     ads[i]
                    #     .find_element_by_css_selector(".MUxGbd.yDYNvb.lyLwlc")
                    #     .text
                    # )
                    self.google_ads["説明文" + str(i + 1)] = (
                        ads[i]
                        .find_element_by_css_selector(".MUxGbd.yDYNvb.lyLwlc")
                        .text
                    )
                except Exception:
                    # self.google_ads.append("")
                    self.google_ads["説明文" + str(i + 1)] = ""
            if i == 0:
                # サイトリンクタイトル
                for index in range(4):
                    try:
                        self.google_ads["サイトリンク" + str(index + 1) + "タイトル"] = (
                            ads[i]
                            .find_elements_by_css_selector("h3 > div > a")[index]
                            .text
                        )
                    except Exception:
                        # self.google_ads.append("")
                        self.google_ads["サイトリンク" + str(index + 1) + "タイトル"] = ""
                # サイトリンク説明文
                nums = [0, 2, 4, 6]
                for index in range(4):
                    try:
                        self.google_ads["サイトリンク" + str(index + 1) + "説明文"] = (
                            ads[i]
                            .find_elements_by_css_selector(".fCBnFe > div")[nums[index]]
                            .text
                            + ads[i]
                            .find_elements_by_css_selector(".fCBnFe > div")[
                                nums[index] + 1
                            ]
                            .text
                        )
                    except Exception:
                        # self.google_ads.append("")
                        self.google_ads["サイトリンク" + str(index + 1) + "説明文"] = ""
        sort_list = [
            "日付",
            "広告タイトル1",
            "広告タイトル2",
            "広告タイトル3",
            "説明文1",
            "説明文2",
            "サイトリンク1タイトル",
            "サイトリンク1説明文",
            "サイトリンク2タイトル",
            "サイトリンク2説明文",
            "サイトリンク3タイトル",
            "サイトリンク3説明文",
            "サイトリンク4タイトル",
            "サイトリンク4説明文",
            "ランディングページ",
        ]
        for i in range(len(sort_list)):
            name = sort_list[i]
            self.google_sort_ads.append(self.google_ads[name])
        self.fetch_img(driver, "google")

    def fetch_yahoo_data(self, driver):
        driver.get(self.yahoo_url)
        sleep(2)
        ads = driver.els_selector(".sw-Card.Ad.js-Ad")
        for el in ads:
            # el.find_element_by_css_selector("h3").text
            self.yahoo_ads.append(el.text)
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
        self.g_drive.create_spreadsheet(self.search_query.replace("+", "_"))
        self.g_drive.append_row(["google検索"])
        for val in self.google_ads:
            self.g_drive.append_row([val])
        self.g_drive.append_row(["yahoo検索"])
        for val in self.yahoo_ads:
            self.g_drive.append_row([val])


def scraping():
    my_scraping = Scraping("ダイソン　セール")
    # my_scraping = Scraping("家電量販店　東京")
    # スクレイピング+グーグルドライブに保存
    my_scraping.scraping()
    my_scraping.write_spread_sheet()


if __name__ == "__main__":
    scraping()
