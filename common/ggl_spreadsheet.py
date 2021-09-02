import gspread
import pandas as pd
from gspread.models import Spreadsheet, Worksheet
from oauth2client.service_account import ServiceAccountCredentials
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

from common.util import fetch_absolute_path, fetch_env

JASON_FILE_NAME = fetch_env("JASON_FILE_NAME")
JSON_PATH = fetch_absolute_path(JASON_FILE_NAME)
SPREAD_SHEET_KEY = fetch_env("SPREAD_SHEET_KEY")


class Gspread:
    def __init__(self) -> None:
        self.workbook: Spreadsheet
        self.worksheet: Worksheet
        self.drive: GoogleDrive
        self.credentials = self.fetch_credentials()
        # self.folder_name: str
        self.new_folder_id: str
        self.df = []

    def fetch_credentials(self):
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            JASON_FILE_NAME, scope
        )
        return credentials

    def create_folder(self, folder_name: str) -> None:
        gauth = GoogleAuth()
        gauth.credentials = self.credentials
        self.drive = GoogleDrive(gauth)
        folder_id = "1aRDY5vSQRVz3hXlWrPr1xHEtv4Ilijz3"
        f_folder = self.drive.CreateFile(
            {
                "title": folder_name,
                "parents": [{"id": folder_id}],
                "mimeType": "application/vnd.google-apps.folder",
            }
        )
        f_folder.Upload()
        self.new_folder_id = self.drive.ListFile(
            {"q": f'title = "{folder_name}"'}
        ).GetList()[0]["id"]

    def create_spreadsheet(self, file_name: str) -> None:
        f = self.drive.CreateFile(
            {
                "title": file_name,
                "mimeType": "application/vnd.google-apps.spreadsheet",
                "parents": [{"id": self.new_folder_id}],
            }
        )
        f.Upload()
        gc = gspread.authorize(self.credentials)
        # ワークシート指定
        self.workbook = gc.open_by_key(f["id"])
        self.worksheet = self.workbook.sheet1

    def save_file(self, local_img_path: str, file_name: str) -> None:
        f = self.drive.CreateFile({"parents": [{"id": self.new_folder_id}]})
        f.SetContentFile(local_img_path + "/" + file_name)
        f["title"] = file_name
        f.Upload()

    def update_cell(self, row: int, column: int, val: str) -> None:
        self.worksheet.update_cell(row, column, val)

    def append_row(self, val: list) -> None:
        self.worksheet.append_row(val)

    def connect_gspread(self):
        try:
            gc = gspread.authorize(self.credentials)
            workbook = gc.open_by_key(SPREAD_SHEET_KEY)
            return workbook
        except Exception:
            print("Googleスプレッドシートを読み込めませんでした。")
            return None

    def read_sheet(self, sheet_num: int):
        # 0番目が一枚目のシート
        self.worksheet = self.workbook.get_worksheet(sheet_num)
        return self.worksheet

    # def read_sheet(self, workbook, sheet_name: str):
    #     self.worksheet = self.workbook.worksheet(sheet_name)

    def set_df(self):
        self.df = pd.DataFrame(self.worksheet.get_all_values())
        self.df.columns = list(self.df.loc[0, :])
        self.df.drop(0, inplace=True)
        self.df.reset_index(inplace=True)
        self.df.drop("index", axis=1, inplace=True)
