from typing import Any

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
SHARE_FOLDER_ID = fetch_env("FOLDER_ID")


class Gspread:
    def __init__(self) -> None:
        self.workbook: Spreadsheet
        self.worksheet: Worksheet
        self.drive: GoogleDrive
        self.credentials: Any
        self.folder_id: str = SHARE_FOLDER_ID
        self.df = []
        self.set_gspread()

    def set_gspread(self):
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        self.credentials = ServiceAccountCredentials.from_json_keyfile_name(
            JASON_FILE_NAME, scope
        )
        gauth = GoogleAuth()
        gauth.credentials = self.credentials
        self.drive = GoogleDrive(gauth)

    def to_folder(self, folder_name: str) -> None:
        # 指定のフォルダに入る（フォルダID作成）

        try:
            # files = self.drive.ListFile(
            #     {"q": f'"{SHARE_FOLDER_ID}" in parents and trashed=false'}
            # ).GetList()[0]
            # for file in files:
            #     if folder_name == file["title"]:
            self.folder_id = self.drive.ListFile(
                {"q": f'title = "{folder_name}"'}
            ).GetList()[0]["id"]
        except Exception:
            # なければフォルダを作る
            f_folder = self.drive.CreateFile(
                {
                    "title": folder_name,
                    "parents": [{"id": SHARE_FOLDER_ID}],
                    "mimeType": "application/vnd.google-apps.folder",
                }
            )
            f_folder.Upload()
            self.folder_id = self.drive.ListFile(
                {"q": f'title = "{folder_name}"'}
            ).GetList()[0]["id"]

    def to_more_folder(self, folder_name: str) -> None:
        """
        作成したフォルダ(folder_id)の中にさらにフォルダを作る
        folder_idは新しく作られたフォルダIDに上書きされる
        """
        old_folder_id = self.folder_id
        f_folder = self.drive.CreateFile(
            {
                "title": folder_name,
                "parents": [{"id": old_folder_id}],
                "mimeType": "application/vnd.google-apps.folder",
            }
        )
        f_folder.Upload()
        self.folder_id = self.drive.ListFile(
            {"q": f'title = "{folder_name}"'}
        ).GetList()[0]["id"]

    def to_spreadsheet(self, file_name: str) -> None:
        # 名前でbookを指定してなければ作る
        gc = gspread.authorize(self.credentials)
        try:
            self.workbook = gc.open(file_name)
        except Exception:
            f = self.drive.CreateFile(
                {
                    "title": file_name,
                    "mimeType": "application/vnd.google-apps.spreadsheet",
                    "parents": [{"id": self.folder_id}],
                }
            )
            f.Upload()
            self.workbook = gc.open_by_key(["id"])
        # ワークシート１シート目指定
        self.worksheet = self.workbook.get_worksheet(0)

    def add_worksheet(self, sheet_name: str):
        self.worksheet = self.workbook.add_worksheet(
            title=sheet_name, rows=100, cols=20
        )

    def rename_sheet(self, new_sheet_name: str):
        self.worksheet.update_title(new_sheet_name)

    def change_sheet(self, sheet_num: int) -> None:
        # シートは0~
        self.worksheet = self.workbook.get_worksheet(sheet_num)

    def save_file(self, local_img_path: str, file_name: str) -> None:
        f = self.drive.CreateFile({"parents": [{"id": self.folder_id}]})
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
