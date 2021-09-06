from datetime import datetime
from time import sleep

import schedule

from common.ggl_spreadsheet import Gspread
from scrape import scraping


class Scrape:
    def __init__(self) -> None:
        self.g_drive = Gspread()
        self.hours: list = []
        self.search_words: list = []

    def is_scrape(self) -> bool:
        self.g_drive.open_sheet_by_(self.g_drive.search_sheet_id)
        self.hours = self.g_drive.fetch_sheet_names()
        dt_now = datetime.now()
        is_scrape = False
        # その時間のシートがあるか確認
        for hour in self.hours:
            if hour == dt_now.strftime("%H"):
                # 対象のシートに切り替え
                self.g_drive.change_sheet_by_name(hour)
                is_scrape = True
        return is_scrape

    def start_scraping(self) -> None:
        df = self.g_drive.set_df()
        # スプレッドシートから検索ワード抽出
        for i, items in df.iterrows():
            self.search_words.append(items[0])
        for s in self.search_words:
            scraping(s)
        print(f"{datetime.now().strftime('%Y/%m/%d %H:%M:%S')}スクレイピング完了")


def start() -> None:
    scrape = Scrape()
    if scrape.is_scrape():
        scrape.start_scraping()


schedule.every().hours.at(":34").do(start)


def main() -> None:
    # jobの実行監視、指定時間になったらjob関数を実行
    while True:
        schedule.run_pending()
        sleep(30)


if __name__ == "__main__":
    main()
