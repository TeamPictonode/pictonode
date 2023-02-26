# GNU AGPL v3 License
# Written by John Nunley

import os
import pytest
import psycopg2
import tempfile

from os import path

from ontario_web import create_app
from ontario_web.db import get_db, init_db

@pytest.fixture
def app():
    test_config = {
      'TESTING': True,
      'DATABASE': 'ontario_test',
      'USER': 'ontario_test',
      'PASSWORD': 'ontario_test',
      'HOST': 'localhost',
      'PORT': '5432'
    }
    app = create_app(test_config)

    with app.app_context():
        init_db(test_config)
        with open(path.join(path.dirname(__file__), "setup.sql"), "r") as f:
            conn = get_db()
            cursor = conn.cursor()
            try:
              cursor.execute(f.read())
              conn.commit()
            except psycopg2.ProgrammingError:
              pass
            finally:
              cursor.close()
              conn.close()

    yield app

@pytest.fixture
def client(app):
    return app.test_client()

