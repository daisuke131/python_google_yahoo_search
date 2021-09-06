from common.ggl_spreadsheet import Gspread
from scrape import scraping


class Scrape:
    def __init__(self) -> None:
        self.g_drive = Gspread()
        self.sheet_names: list = []
        self.search_words: list = []

    def fetch_search_words(self) -> None:
        self.g_drive.open_sheet_by_(self.g_drive.search_sheet_id)
        self.sheet_names = self.g_drive.fetch_sheet_names()
        # その時間のシートがあるか確認
        for name in self.sheet_names:
            self.g_drive.change_sheet_by_name(name)
            df = self.g_drive.set_df()
            for i, items in df.iterrows():
                self.search_words.append(items[0])
        self.search_words = list(set(self.search_words))

    def start_scraping(self) -> None:
        for s in self.search_words:
            scraping(s)


def main() -> None:
    scrape = Scrape()
    scrape.fetch_search_words()
    scrape.start_scraping()


if __name__ == "__main__":
    main()
