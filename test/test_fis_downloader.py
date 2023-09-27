from datetime import date
import pytest
from ..fis_downloader import FISReport


@pytest.fixture
def fis_report() -> FISReport:
    return FISReport(date(2023, 9, 20), "FFA")


def test_fisreport_geturl(fis_report):
    assert (
        fis_report.get_url()
        == "https://fisapp.com/wp-content/uploads/2023/09/CapePMX-Report-200923.pdf"
    )


def test_fisreport_download(fis_report):
    assert fis_report.download() == True


def test_fisreport_check_exist(fis_report):
    assert fis_report.check_exist() == True
