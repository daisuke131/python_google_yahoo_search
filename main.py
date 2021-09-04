# from time import sleep

from common.ggl_spreadsheet import Gspread
from scrape import scraping

# import schedule


class Scrape:
    def __init__(self) -> None:
        self.g_drive = Gspread()
        self.search_word_list: list = []

    def read_search_spread_sheet(self):
        self.g_drive.open_sheet_by_(self.g_drive.search_sheet_id)
        df = self.g_drive.set_df()
        for index, items in df.iterrows():
            self.search_word_list.append(items[0])

    def start_scraping(self):
        for s in self.search_word_list:
            scraping(s)


def main():
    scrape = Scrape()
    scrape.read_search_spread_sheet()
    scrape.start_scraping()


# # 実行job関数
# def job():
#     sleep(5)
#     print("job実行")


# # 1分毎のjob実行を登録
# schedule.every(1).minutes.do(job)

# # 1時間毎のjob実行を登録
# schedule.every(1).hours.do(job)

# # AM11:00のjob実行を登録
# schedule.every().day.at("11:00").do(job)

# # 日曜日のjob実行を登録
# schedule.every().sunday.do(job)

# # 水曜日13:15のjob実行を登録
# schedule.every().wednesday.at("13:15").do(job)

# # jobの実行監視、指定時間になったらjob関数を実行
# while True:
#     schedule.run_pending()
#     sleep(1)

if __name__ == "__main__":
    main()
