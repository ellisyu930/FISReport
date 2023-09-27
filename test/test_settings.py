from ..settings import get_settings


def test_get_settings():
    settings = get_settings()
    assert settings.FIS_BASE_URL == "https://fisapp.com/wp-content/uploads"
    assert settings.FIS_FILENAME_PREFIX["FFA"] == "CapePMX-Report"
