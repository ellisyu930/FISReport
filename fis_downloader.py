from settings import get_settings, DevSettings, ProdSettings
from datetime import date
import requests


class FISReport:
    def __init__(self, report_date: date, report_name) -> None:
        self.report_date = report_date
        self.name = report_name
        self.content = None
        self.setting = get_settings()

    def get_url(self) -> str:
        base_url = self.setting.FIS_BASE_URL
        year = self.report_date.year
        month: str = self.report_date.strftime("%m")
        path = f"{year}/{month}"
        filename_prefix_list: dict[str:str] = self.setting.FIS_FILENAME_PREFIX
        filename_prefix = filename_prefix_list[self.name]
        date_format: str = self.setting.RPT_DATE_FORMAT
        filename_suffix: str = self.report_date.strftime(date_format)
        full_url = f"{base_url}/{path}/{filename_prefix}-{filename_suffix}.pdf"

        return full_url

    def check_exist(self) -> bool:
        response = requests.get(self.get_url())
        # Check if the response status code is 200 (OK)
        if response.status_code == 200:
            return True

    def download(self) -> bool:
        response = requests.get(self.get_url())
        # Check if the response status code is 200 (OK)
        if response.status_code == 200:
            self.content = response.content
            return True
        return False
