import os

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.utils import ChromeType

from common.util import fetch_user_agent

BROWSER_NAME: str = "chrome"


class Driver:
    def __init__(self, headless_flg: bool = True):
        self.driver = self.driver_setting(headless_flg)

    def driver_setting(self, headless_flg: bool):
        user_agent_random = fetch_user_agent()
        # ドライバーの読み込み
        if "firefox" in BROWSER_NAME:
            options = webdriver.FirefoxOptions()
        else:
            options = webdriver.ChromeOptions()

        # ヘッドレスモードの設定
        if os.name == "posix" or headless_flg:  # Linux　➙　本番環境のためHeadless
            options.add_argument("--headless")

        options.add_argument("--user-agent=" + user_agent_random)
        options.add_argument("log-level=3")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--ignore-ssl-errors")
        options.add_argument("--incognito")  # シークレットモードの設定を付与
        options.add_argument("--disable-extensions")  # 全ての拡張機能無効
        options.add_argument("disable-infobars")  # AmazonLinux用
        # options.add_argument("--start-maximized") # 画面最大化
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-desktop-notifications")
        options.add_argument("--disable-application-cache")
        options.add_argument("--lang=ja")
        # 画像を読み込まないで軽くする
        # options.add_argument("--blink-settings=imagesEnabled=false")

        try:
            if "firefox" in BROWSER_NAME:
                driver = webdriver.Firefox(
                    executable_path=GeckoDriverManager().install(), options=options
                )
            elif "chromium" in BROWSER_NAME:
                driver = webdriver.Chrome(
                    ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install(),
                    options=options,
                )
            else:
                driver = webdriver.Chrome(
                    ChromeDriverManager().install(), options=options
                )
            return driver
        except Exception:
            return None

    def get(self, url: str) -> None:
        self.driver.get(url)

    def el_selector(self, s: str):
        return self.driver.find_element_by_css_selector(s)

    def els_selector(self, s: str):
        return self.driver.find_elements_by_css_selector(s)

    def el_id(self, s: str):
        return self.driver.find_element_by_id(s)

    def els_id(self, s: str):
        return self.driver.find_elements_by_id(s)

    def el_class(self, s: str):
        return self.driver.find_element_by_class_name(s)

    def els_class(self, s: str):
        return self.driver.find_elements_by_class_name(s)

    def el_xpath(self, s: str):
        return self.driver.find_element_by_xpath(s)

    def els_xpath(self, s: str):
        return self.driver.find_elements_by_xpath(s)

    def script_click(self, s: str):
        return self.driver.execute_script(f"document.querySelector({s}).click()")

    def save_screenshot(self, path: str, img_name: str):
        w = self.driver.execute_script("return document.body.scrollWidth;")
        h = self.driver.execute_script("return document.body.scrollHeight;")
        self.driver.set_window_size(w, h)
        self.driver.save_screenshot(path + "/" + img_name)

    def quit(self):
        return self.driver.quit()
