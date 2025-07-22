from project import create_app # create_app: Factory function to create a Flask app instance
from project.db import db # db: SQLAlchemy database instance for ORM operations
import pytest # pytest: Testing framework used for fixtures and test discovery

@pytest.mark.last
def test_app_loads_config_from_file():
    # Create app WITHOUT passing test_config so it loads from config.py
    fresh_app = create_app()

    # Now assert some known config value from your config.py
    # For example, if config.py sets DEBUG = False or any other setting
    assert fresh_app.config.get("DEBUG") is not None  # or specific expected value
    assert fresh_app.config.get('RATELIMIT_DEFAULT') == "30 per hour"
    assert fresh_app.config.get('WTF_CSRF_ENABLED')