"""Re-export fixtures from api/tests/conftest.py for integration tests."""

# Pull in all fixtures defined in the API test suite so integration tests
# can use the same client, populated_db, sample_archive_zip, etc.
pytest_plugins = ["api.tests.conftest"]
