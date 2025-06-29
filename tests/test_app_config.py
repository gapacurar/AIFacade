from project import create_app
import pytest

@pytest.mark.last
def test_app_loads_config_from_file():
    # Create app WITHOUT passing test_config so it loads from config.py
    fresh_app = create_app()

    # Now assert some known config value from your config.py
    # For example, if config.py sets DEBUG = False or any other setting
    assert fresh_app.config.get("DEBUG") is not None  # or specific expected value
    assert fresh_app.config.get('RATELIMIT_DEFAULT') == "5 per minute"
    assert fresh_app.config.get('WTF_CSRF_ENABLED')