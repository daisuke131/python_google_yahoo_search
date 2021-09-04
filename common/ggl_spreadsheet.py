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
SHARE_FOLDER_ID = fetch_env("FOLDER_ID")  # 親フォルダのfileid
SPREAD_SHEET_ID = fetch_env("SHEET_ID")  # 検索ワードのスプレッドシートID


class Gspread:
    def __init__(self) -> None:
        self.workbook: Spreadsheet
        self.worksheet: Worksheet
        self.drive: GoogleDrive
        self.credentials: Any
        # 他のフォルダのfile_idはメインの方で持たす
        # なので新たにフォルダを作ったときフォルダのファイルIDを返す
        self.parent_folder_id: str = SHARE_FOLDER_ID
        self.search_sheet_id: str = SPREAD_SHEET_ID
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

    def to_folder_by_folder_name(
        self, folder_id: str, folder_name: str
    ) -> list[str, bool]:
        # folderに移動するというよりfile_idを取得している
        is_create_folder: bool = True
        new_folder_id: str
        try:
            files = self.drive.ListFile(
                {"q": f'"{folder_id}" in parents and trashed=false'}
            ).GetList()
            for file in files:
                if folder_name == file["title"]:
                    is_create_folder = False
                    # フォルダID指定
                    new_folder_id = file["id"]
                    break
            if is_create_folder:
                f_folder = self.drive.CreateFile(
                    {
                        "title": folder_name,
                        "parents": [{"id": folder_id}],
                        "mimeType": "application/vnd.google-apps.folder",
                    }
                )
                f_folder.Upload()
                new_folder_id = f_folder["id"]
            # 新しくフォルダを作成したかを返す
            return new_folder_id, is_create_folder
        except Exception as e:
            print(e)

    def to_more_folder(self, folder_id: str, folder_name: str) -> None:
        """
        作成したフォルダ(folder_id)の中にさらにフォルダを作る
        folder_idは新しく作られたフォルダIDに上書きされる
        """
        # old_folder_id = self.folder_id
        f_folder = self.drive.CreateFile(
            {
                "title": folder_name,
                "parents": [{"id": folder_id}],
                "mimeType": "application/vnd.google-apps.folder",
            }
        )
        f_folder.Upload()
        return f_folder["id"]

    def delete_folder(self, folder_name: str):
        folder_id = self.drive.ListFile({"q": f'title = "{folder_name}"'}).GetList()[0][
            "id"
        ]
        f_file = self.drive.CreateFile({"id": folder_id})
        f_file.Delete()

    def to_spreadsheet(self, folder_id: str, file_name: str) -> bool:
        # 名前でbookを指定してなければ作る
        gc = gspread.authorize(self.credentials)
        is_create_workbook = True
        try:
            files = self.drive.ListFile(
                {"q": f'"{folder_id}" in parents and trashed=false'}
            ).GetList()
            for file in files:
                if file_name == file["title"]:
                    is_create_workbook = False
                    # ワークブック指定
                    self.workbook = gc.open_by_key(file["id"])
                    break
            if is_create_workbook:
                file = self.drive.CreateFile(
                    {
                        "title": file_name,
                        "mimeType": "application/vnd.google-apps.spreadsheet",
                        "parents": [{"id": folder_id}],
                    }
                )
                file.Upload()
                # ワークブック指定
                self.workbook = gc.open_by_key(file["id"])
            # ワークシート１シート目指定
            self.worksheet = self.workbook.get_worksheet(0)
            # 新しくworkbookを作成したかを返す
            return is_create_workbook
        except Exception as e:
            print(e)

    def add_worksheet(self, sheet_name: str):
        self.worksheet = self.workbook.add_worksheet(
            title=sheet_name, rows=100, cols=20
        )

    def rename_sheet(self, new_sheet_name: str):
        self.worksheet.update_title(new_sheet_name)

    def change_sheet(self, sheet_num: int) -> None:
        # シートは0~
        self.worksheet = self.workbook.get_worksheet(sheet_num)

    def save_file(self, folder_id: str, local_img_path: str, file_name: str) -> None:
        f = self.drive.CreateFile({"parents": [{"id": folder_id}]})
        f.SetContentFile(local_img_path + "/" + file_name)
        f["title"] = file_name
        f.Upload()

    def update_cell(self, row: int, column: int, val: str) -> None:
        self.worksheet.update_cell(row, column, val)

    def append_row(self, val: list) -> None:
        self.worksheet.append_row(val)

    def open_sheet_by_(self, file_id: str):
        try:
            gc = gspread.authorize(self.credentials)
            self.workbook = gc.open_by_key(file_id)
            # ワークシート１シート目指定
            self.worksheet = self.workbook.get_worksheet(0)
        except Exception:
            print("Googleスプレッドシートを読み込めませんでした。")

    def set_df(self):
        df = pd.DataFrame(self.worksheet.get_all_values())
        # ヘッダーが一行目データになっているのでちゃんとヘッダーにする
        df.columns = list(df.loc[0, :])
        df.drop(0, inplace=True)
        df.reset_index(inplace=True)
        df.drop("index", axis=1, inplace=True)
        return df

    def fetch_wb_url(self):
        return self.workbook.url + "/edit?usp=sharing"
