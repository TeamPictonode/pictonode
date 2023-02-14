# GNU AGPL v3 License
# Written by John Nunley

import os
import pytest
import tempfile

from ontario_web import create_app

@pytest.fixture
def app():
    app = create_app({
      'TESTING': True,
    })

    yield app

@pytest.fixture
def client(app):
    return app.test_client()

