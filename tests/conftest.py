import os
import sys
import pytest
import warnings
from app.database import init_db

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture(autouse=True)
def setup_db():
    # Initialize the database before tests
    init_db()
    yield