import pytest


@pytest.fixture(autouse=True)
def alarm_client_logging_config(monkeypatch):
    monkeypatch.setenv('LOG_LEVEL', 'ERROR')
