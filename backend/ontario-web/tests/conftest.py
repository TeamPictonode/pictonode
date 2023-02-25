# GNU AGPL v3 License
# Written by John Nunley

import os
import pytest
import tempfile

from os import path

from ontario_web import create_app
from ontario_web.db import get_db, init_db

@pytest.fixture
def app():
    app = create_app({
      'TESTING': True,
      'DATABASE': 'ontario_test'
    })

    with app.app_context():
        init_db()
        with open(path.join(path.dirname(__file__), "setup.sql"), "r") as f:
            get_db().executescript(f.read())

    yield app

@pytest.fixture
def client(app):
    return app.test_client()

