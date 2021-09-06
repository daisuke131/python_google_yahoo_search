import shutil
from pathlib import Path
from time import sleep

import pandas as pd

from common.chat_work import send_img
from common.driver import Driver
from common.ggl_spreadsheet import Gspread
from common.util import fetch_absolute_path, hyphen_now, time_now

SS_FOLDER_PATH = fetch_absolute_path("screenshot")
COLUMN_LIST = [
    "日付",
    "広告タイトル1",
    "広告タイトル2",
    "広告タイトル3",
    "説明文",
    "サイトリンク1タイトル",
    "サイトリンク1URL",
    "サイトリンク1説明文",
    "サイトリンク2タイトル",
    "サイトリンク2URL",
    "サイトリンク2説明文",
    "サイトリンク3タイトル",
    "サイトリンク3URL",
    "サイトリンク3説明文",
    "サイトリンク4タイトル",
    "サイトリンク4URL",
    "サイトリンク4説明文",
    "ランディングページ",
]
GOOGLE_SHOPPING_COLUMN_LIST = ["日付", "商品名", "価格", "店舗名", "送料", "ランディングページ"]


class Scraping:
    def __init__(self, search_word: str) -> None:
        self.g_drive = Gspread()
        self.driver = Driver()
        self.search_query: str = self.fetch_query(search_word)
        self.google_url: str = self.fetch_google_url()
        self.yahoo_url: str = self.fetch_yahoo_url()
        self.google_store_ads: list = []
        self.google_ads = pd.DataFrame()
        self.yahoo_ads = pd.DataFrame()
        self.spreadsheet_url: str
        self.nowdate = hyphen_now()  # 2021-09-10-00-00-00
        self.nowdatetime = time_now()  # 2021/09/10 00:00:00
        # googleドライブのフォルダID
        self.search_foler_id: str
        self.google_foler_id: str
        self.yahoo_foler_id: str

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

    def fetch_google_ads_data(self) -> None:
        self.driver.get(self.google_url)
        sleep(3)
        # スクショ保存
        self.save_img_to_local("google")
        # ショップ広告
        self.fetch_google_shop_ads_data()
        # 普通の広告
        ads = self.driver.els_selector(".cUezCb.luh4tb.O9g5cc.uUPGi")
        for el in ads:
            titles = self.fetch_google_ads_title(el)
            (
                site_link_titles,
                site_link_urls,
                site_link_texts,
            ) = self.fetch_google_ads_site_link(el)
            self.google_ads = self.google_ads.append(
                {
                    "日付": self.nowdatetime,
                    "広告タイトル1": titles[0],
                    "広告タイトル2": titles[1],
                    "広告タイトル3": titles[2],
                    "説明文": self.fetch_google_ads_explanatorytext(el),
                    "サイトリンク1タイトル": site_link_titles[0],
                    "サイトリンク1URL": site_link_urls[0],
                    "サイトリンク1説明文": site_link_texts[0],
                    "サイトリンク2タイトル": site_link_titles[1],
                    "サイトリンク2URL": site_link_urls[1],
                    "サイトリンク2説明文": site_link_texts[1],
                    "サイトリンク3タイトル": site_link_titles[2],
                    "サイトリンク3URL": site_link_urls[2],
                    "サイトリンク3説明文": site_link_texts[2],
                    "サイトリンク4タイトル": site_link_titles[3],
                    "サイトリンク4URL": site_link_urls[3],
                    "サイトリンク4説明文": site_link_texts[3],
                    "ランディングページ": el.find_element_by_css_selector(
                        ".Krnil"
                    ).get_attribute("href"),
                },
                ignore_index=True,
            )

    def fetch_google_ads_title(self, el) -> list:
        # google広告タイトル取得
        try:
            title = el.find_element_by_css_selector("div > span").text
            titles = title.split(" - ")
            if len(titles) == 1:
                titles.extend(["", ""])
            elif len(titles) == 2:
                titles.append("")
            return titles
        except Exception:
            return "", "", ""

    def fetch_google_ads_explanatorytext(self, el) -> str:
        # google説明文取得
        try:
            return el.find_element_by_css_selector(".MUxGbd.yDYNvb.lyLwlc").text[:180]
        except Exception:
            return ""

    def fetch_google_ads_site_link(self, el) -> list:
        # サイトリンクデータ取得
        site_link_titles = []
        site_link_urls = []
        site_link_texts = []
        nums = [0, 2, 4, 6]
        for index in range(4):
            # タイトル
            try:
                site_link_titles.append(
                    el.find_elements_by_css_selector("h3 > div > a")[index].text
                )
            except Exception:
                site_link_titles.append("")
            # リンクURL
            try:
                site_link_urls.append(
                    el.find_elements_by_css_selector("h3 > div > a")[
                        index
                    ].get_attribute("href")
                )
            except Exception:
                site_link_urls.append("")
            # 説明文
            try:
                site_link_texts.append(
                    el.find_elements_by_css_selector(".fCBnFe > div")[nums[index]].text
                    + el.find_elements_by_css_selector(".fCBnFe > div")[
                        nums[index] + 1
                    ].text
                )
            except Exception:
                site_link_texts.append("")

        return site_link_titles, site_link_urls, site_link_texts

    def fetch_google_shop_ads_data(self) -> None:
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

    def fetch_yahoo_data(self) -> None:
        self.driver.get(self.yahoo_url)
        sleep(3)
        # スクショ保存
        self.save_img_to_local("yahoo")
        # 広告情報抽出
        ads = self.driver.els_selector(".sw-Card.Ad.js-Ad")
        for el in ads:
            titles = self.fetch_yahoo_ads_title(el)
            (
                site_link_titles,
                site_link_urls,
                site_link_texts,
            ) = self.fetch_yahoo_ads_site_link(el)
            self.yahoo_ads = self.yahoo_ads.append(
                {
                    "日付": self.nowdatetime,
                    "広告タイトル1": titles[0],
                    "広告タイトル2": titles[1],
                    "広告タイトル3": titles[2],
                    "説明文": self.fetch_yahoo_ads_explanatorytext(el),
                    "サイトリンク1タイトル": site_link_titles[0],
                    "サイトリンク1URL": site_link_urls[0],
                    "サイトリンク1説明文": site_link_texts[0],
                    "サイトリンク2タイトル": site_link_titles[1],
                    "サイトリンク2URL": site_link_urls[1],
                    "サイトリンク2説明文": site_link_texts[1],
                    "サイトリンク3タイトル": site_link_titles[2],
                    "サイトリンク3URL": site_link_urls[2],
                    "サイトリンク3説明文": site_link_texts[2],
                    "サイトリンク4タイトル": site_link_titles[3],
                    "サイトリンク4URL": site_link_urls[3],
                    "サイトリンク4説明文": site_link_texts[3],
                    "ランディングページ": el.find_element_by_css_selector(
                        ".sw-Card__title > a"
                    ).get_attribute("href"),
                },
                ignore_index=True,
            )

    def fetch_yahoo_ads_title(self, el) -> list:
        # yahoo広告タイトル取得
        try:
            title = el.find_element_by_css_selector("h3").text
            titles = title.split(" - ")
            if len(titles) == 1:
                titles.extend(["", ""])
            elif len(titles) == 2:
                titles.append("")
            return titles
        except Exception:
            return "", "", ""

    def fetch_yahoo_ads_explanatorytext(self, el) -> str:
        # google説明文取得
        try:
            return el.find_element_by_css_selector(".sw-Card__summary").text[:180]
        except Exception:
            return ""

    def fetch_yahoo_ads_site_link(self, el) -> list:
        # サイトリンクデータ取得
        site_link_titles = []
        site_link_urls = []
        site_link_texts = []
        for index in range(4):
            # タイトル
            try:
                site_link_titles.append(
                    el.find_elements_by_css_selector(
                        ".sw-Link.Ad__siteLinks > div > ul > li > a"
                    )[index].text
                )
            except Exception:
                site_link_titles.append("")
            # リンクURL
            try:
                site_link_urls.append(
                    el.find_elements_by_css_selector(
                        ".sw-Link.Ad__siteLinks > div > ul > li > a"
                    )[index].get_attribute("href")
                )
            except Exception:
                site_link_urls.append("")
            # 説明文
            try:
                site_link_texts.append(
                    el.find_elements_by_css_selector(
                        ".sw-Link.Ad__siteLinks > div > ul > li > span"
                    )[index].text
                )
            except Exception:
                site_link_texts.append("")

        return site_link_titles, site_link_urls, site_link_texts

    def save_img_to_local(self, search_kind: str) -> None:
        # screenshotフォルダがない場合は作る
        dir = Path(SS_FOLDER_PATH)
        dir.mkdir(parents=True, exist_ok=True)
        # スクショして一時的にローカルフォルダに保存
        self.driver.save_screenshot(SS_FOLDER_PATH, f"{self.nowdate}_{search_kind}.jpg")

    def save_img_to_googledrive(self) -> None:
        # googleドライブに保存
        self.g_drive.save_file(
            self.google_foler_id, SS_FOLDER_PATH, f"{self.nowdate}_google.jpg"
        )
        self.g_drive.save_file(
            self.yahoo_foler_id, SS_FOLDER_PATH, f"{self.nowdate}_yahoo.jpg"
        )

    def write_spread_sheet(self) -> None:
        """
        検索ワード名のワークシートがなければ作成
        検索ワード初回のみ作成
        """
        self.g_drive.to_spreadsheet(
            self.search_foler_id, self.search_query.replace("+", "_")
        )
        """
        新規でスプレッドシートを作成した場合、
        ワークシートを作る。
        """
        if len(self.g_drive.workbook.worksheets()) < 3:
            # google広告ヘッダー作成
            self.g_drive.append_row(COLUMN_LIST)
            # 1つ目のシートはすでにあるのでリネーム
            self.g_drive.rename_sheet("google広告")
            # シート作成
            self.g_drive.add_worksheet("googleショッピング広告")
            # googleショピング広告ヘッダー作成
            self.g_drive.append_row(GOOGLE_SHOPPING_COLUMN_LIST)
            # シート作成
            self.g_drive.add_worksheet("yahoo広告")
            # yahoo広告ヘッダー作成
            self.g_drive.append_row(COLUMN_LIST)
        # google広告書き込み
        self.g_drive.change_sheet_by_num(0)
        for i in range(len(self.google_ads)):
            self.g_drive.append_row(self.google_ads.iloc[i].to_list())
        """
        googleショッピング広告書き込み
        2シート目へ移動
        """
        self.g_drive.change_sheet_by_num(1)
        for val in self.google_store_ads:
            self.g_drive.append_row(val)
        """
        yahoo広告書き込み
        3シート目へ移動
        """
        self.g_drive.change_sheet_by_num(2)
        for i in range(len(self.yahoo_ads)):
            self.g_drive.append_row(self.yahoo_ads.iloc[i].to_list())
        """
        URL取得
        """
        self.spreadsheet_url = self.g_drive.fetch_wb_url()

    def make_folder(self) -> None:
        """
        Googleドライブの中でフォルダを作成
        フォルダ名は検索ワード
        初めての検索ワードのときだけ作成される。
        """
        (
            self.search_foler_id,
            is_create_folder,
        ) = self.g_drive.to_folder_by_folder_name(
            self.g_drive.parent_folder_id, self.search_query.replace("+", "_")
        )
        if is_create_folder:
            # 画像用フォルダを作る
            self.g_drive.to_more_folder(self.search_foler_id, "google")
            self.g_drive.to_more_folder(self.search_foler_id, "yahoo")
        # googleとyahooフォルダのID取得
        self.google_foler_id = self.g_drive.to_folder_by_folder_name(
            self.search_foler_id, "google"
        )[0]
        self.yahoo_foler_id = self.g_drive.to_folder_by_folder_name(
            self.search_foler_id, "yahoo"
        )[0]

    def send_chatwork(self) -> None:
        send_img(
            message=self.spreadsheet_url,
            img_folder=SS_FOLDER_PATH,
            imag_name=f"{self.nowdate}_google.jpg",
        )
        sleep(1)
        send_img(
            message="", img_folder=SS_FOLDER_PATH, imag_name=f"{self.nowdate}_yahoo.jpg"
        )


def scraping(search_word: str) -> None:
    # スクレイピング用のクラス設定
    my_scraping = Scraping(search_word)
    # googleのデータ抽出
    my_scraping.fetch_google_ads_data()
    # yahooのデータ抽出
    my_scraping.fetch_yahoo_data()
    # 必要ならフォルダ作成
    my_scraping.make_folder()
    # スプレッドシートに書き込み
    my_scraping.write_spread_sheet()
    # googleドライブに画像保存
    my_scraping.save_img_to_googledrive()
    # チャットワークに送信
    my_scraping.send_chatwork()
    # ローカルのスクショフォルダごと削除
    shutil.rmtree(SS_FOLDER_PATH)
