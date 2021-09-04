import os
from pathlib import Path
from time import sleep

from common.chat_work import send_img
from common.driver import Driver
from common.ggl_spreadsheet import Gspread
from common.util import fetch_absolute_path, hyphen_now, time_now

SS_FOLDER_PATH = fetch_absolute_path("screenshot")
dir = Path(SS_FOLDER_PATH)
dir.mkdir(parents=True, exist_ok=True)
GOOGLE_SORT_LIST = [
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
GOOGLE_SHOPPING_SORT_LIST = ["日付", "商品名", "価格", "店舗名", "送料", "ランディングページ"]
YAHOO_SORT_LIST = [
    "日付",
    "広告タイトル1",
    "広告タイトル2",
    "広告タイトル3",
    "説明文1",
    "説明文2",
    "ランディングページ",
]


class Scraping:
    def __init__(self, search_word: str) -> None:
        self.g_drive = Gspread()
        self.driver = Driver()
        self.search_query: str = self.fetch_query(search_word)
        self.google_url: str = self.fetch_google_url()
        self.yahoo_url: str = self.fetch_yahoo_url()
        self.google_store_ads: list = []
        self.google_ads: dict = {}
        self.google_sort_ads: list = []
        self.yahoo_ads: dict = {}
        self.yahoo_sort_ads: list = []
        self.spreadsheet_url: str
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

    def fetch_google_ads_data(self):
        self.driver.get(self.google_url)
        sleep(3)
        # スクショ保存
        self.save_img_to_local("google")
        # ショップ広告
        shop_ads = self.driver.els_selector(".mnr-c.pla-unit")
        for i, ad in enumerate(shop_ads):
            shop_ads_list = []
            # 日時
            shop_ads_list.append(self.nowdatetime)
            #  タイトル
            try:
                shop_ads_list.append(ad.find_element_by_css_selector(".pymv4e").text)
            except Exception:
                break
            # 金額
            shop_ads_list.append(ad.find_element_by_css_selector(".e10twf.T4OwTb").text)
            # ショップ名
            shop_ads_list.append(ad.find_element_by_css_selector(".LbUacb").text)
            # 送料無料
            try:
                shop_ads_list.append(ad.find_element_by_css_selector(".cYBBsb").text)
            except Exception:
                shop_ads_list.append("")
            self.google_store_ads.append(shop_ads_list)
            # URL
            shop_ads_list.append(
                ad.find_element_by_css_selector(f"#vplaurlg{i}").get_attribute("href")
            )

        # 普通の広告
        ads = self.driver.els_selector(".cUezCb.luh4tb.O9g5cc.uUPGi")
        if len(ads) > 0:
            self.google_ads["日付"] = self.nowdatetime
            self.google_ads["ランディングページ"] = self.driver.el_selector(
                ".Zu0yb.LWAWHf.OSrXXb.qzEoUe"
            ).text
            for i in range(3):
                # タイトル
                if i == 0 or i == 1 or i == 2:
                    try:
                        self.google_ads["広告タイトル" + str(i + 1)] = (
                            ads[i].find_element_by_css_selector("div > span").text
                        )
                    except Exception:
                        self.google_ads["広告タイトル" + str(i + 1)] = ""
                # 説明文
                if i == 0 or i == 1:
                    try:
                        self.google_ads["説明文" + str(i + 1)] = (
                            ads[i]
                            .find_element_by_css_selector(".MUxGbd.yDYNvb.lyLwlc")
                            .text
                        )
                    except Exception:
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
                            self.google_ads["サイトリンク" + str(index + 1) + "タイトル"] = ""
                    # サイトリンク説明文
                    nums = [0, 2, 4, 6]
                    for index in range(4):
                        try:
                            self.google_ads["サイトリンク" + str(index + 1) + "説明文"] = (
                                ads[i]
                                .find_elements_by_css_selector(".fCBnFe > div")[
                                    nums[index]
                                ]
                                .text
                                + ads[i]
                                .find_elements_by_css_selector(".fCBnFe > div")[
                                    nums[index] + 1
                                ]
                                .text
                            )
                        except Exception:
                            self.google_ads["サイトリンク" + str(index + 1) + "説明文"] = ""
            # 表示順番入れ替え
            for i in range(len(GOOGLE_SORT_LIST)):
                name = GOOGLE_SORT_LIST[i]
                self.google_sort_ads.append(self.google_ads[name])

    def fetch_yahoo_data(self):
        self.driver.get(self.yahoo_url)
        sleep(3)
        # スクショ保存
        self.save_img_to_local("yahoo")
        # 広告情報抽出
        ads = self.driver.els_selector(".sw-Card.Ad.js-Ad")
        if len(ads) > 0:
            self.yahoo_ads["日付"] = self.nowdatetime
            self.yahoo_ads["ランディングページ"] = self.driver.el_selector(
                ".sw-Card__title > a"
            ).get_attribute("href")
            for i in range(3):
                # タイトル
                try:
                    self.yahoo_ads["広告タイトル" + str(i + 1)] = (
                        ads[i].find_element_by_css_selector("h3").text
                    )
                except Exception:
                    self.yahoo_ads["広告タイトル" + str(i + 1)] = ""
                # 説明文
                if i == 0 or i == 1:
                    try:
                        self.yahoo_ads["説明文" + str(i + 1)] = (
                            ads[i]
                            .find_element_by_css_selector(".sw-Card__summary")
                            .text
                        )
                    except Exception:
                        self.yahoo_ads["説明文" + str(i + 1)] = ""
            # 表示順番入れ替え
            for i in range(len(YAHOO_SORT_LIST)):
                name = YAHOO_SORT_LIST[i]
                self.yahoo_sort_ads.append(self.yahoo_ads[name])

    def save_img_to_local(self, search_kind: str):
        # スクショして一時的にローカルフォルダに保存
        self.driver.save_screenshot(SS_FOLDER_PATH, f"{search_kind}.png")

    def save_img_to_googledrive(self):
        # スクショして一時的にローカルフォルダに保存
        self.g_drive.save_file(SS_FOLDER_PATH, "google.png")
        self.g_drive.save_file(SS_FOLDER_PATH, "yahoo.png")
        # # ローカル画像ファイル削除
        # os.remove(SS_FOLDER_PATH + "/" + "google.png")
        # os.remove(SS_FOLDER_PATH + "/" + "yahoo.png")

    def write_spread_sheet(self):
        """
        検索ワード名のワークシートがなければ作成
        検索ワード初回のみ作成
        """
        self.g_drive.to_spreadsheet(self.search_query.replace("+", "_"))
        """
        スプレッドシートを作成した場合、
        ヘッダーを作成
        """

        """
        新規でスプレッドシートを作成した場合、
        ワークシートを作る。
        """
        if len(self.g_drive.workbook.worksheets()) < 3:
            self.g_drive.append_row(GOOGLE_SORT_LIST)
            # 1つ目のシートはすでにあるのでリネーム
            self.g_drive.rename_sheet("google広告")
            self.g_drive.add_worksheet("googleショッピング広告")
            self.g_drive.append_row(GOOGLE_SHOPPING_SORT_LIST)
            self.g_drive.add_worksheet("yahoo広告")
            self.g_drive.append_row(YAHOO_SORT_LIST)
        # google広告書き込み
        self.g_drive.change_sheet(0)
        # for val in self.google_sort_ads:
        self.g_drive.append_row(self.google_sort_ads)
        """
        googleショッピング広告書き込み
        2シート目へ移動
        """
        self.g_drive.change_sheet(1)
        for val in self.google_store_ads:
            self.g_drive.append_row(val)
        """
        yahoo広告書き込み
        3シート目へ移動
        """
        self.g_drive.change_sheet(2)
        # for val in self.yahoo_sort_ads:
        self.g_drive.append_row(self.yahoo_sort_ads)
        """
        URL取得
        """
        self.spreadsheet_url = self.g_drive.fetch_wb_url()

    def send_chatwork(self):
        send_img(
            message=self.spreadsheet_url,
            img_folder=SS_FOLDER_PATH,
            imag_name="google.png",
        )
        send_img(message="", img_folder=SS_FOLDER_PATH, imag_name="yahoo.png")


def scraping():
    # スクレイピング用のクラス設定
    # my_scraping = Scraping("ダイソン　セール")
    my_scraping = Scraping("冷蔵庫　セール")
    # my_scraping = Scraping("家電量販店　東京")
    # googleのデータ抽出
    my_scraping.fetch_google_ads_data()
    # yahooのデータ抽出
    my_scraping.fetch_yahoo_data()
    """
     Googleドライブの中でフォルダを作成
     フォルダ名は検索ワード
     初めての検索ワードのときだけ作成される。
    """
    my_scraping.g_drive.to_folder(my_scraping.search_query.replace("+", "_"))
    # スプレッドシートに書き込み
    my_scraping.write_spread_sheet()
    """
     スクショ用フォルダ名は2020-04-04-04-00-00-00のように
     ハイフン区切りの日時で命名される
     こちらは検索都度作成される
    """
    my_scraping.g_drive.to_more_folder(my_scraping.nowdate)
    # googleドライブに画像保存
    my_scraping.save_img_to_googledrive()
    # チャットワークに送信
    my_scraping.send_chatwork()
    # ＵＲＬと画像

    # ローカルのスクショ削除
    os.remove(SS_FOLDER_PATH + "/" + "google.png")
    os.remove(SS_FOLDER_PATH + "/" + "yahoo.png")


if __name__ == "__main__":
    scraping()
