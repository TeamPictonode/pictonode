# GNU AGPL v3 License
# Written by John Nunley

import pytest
import psycopg2
import shutil
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


@pytest.fixture
def image_ids(client):
    # Upload it to the client twice
    # Note: /api/upload_image takes a form with a file named "image"
    def upload_image(p):
        data = dict(
            image=(open(p, 'rb'), p)
        )
        response = client.post(
            '/api/upload_image',
            content_type='multipart/form-data',
            data=data
        )
        assert response.status_code == 200
        return response.json['id']

    p1 = path.join(path.dirname(__file__), "assets", "test1.png")
    p2 = path.join(path.dirname(__file__), "assets", "test2.png")

    # Copy the file to a temporary location
    # This is necessary because the file is opened in the upload_image function
    # and cannot be opened again
    with tempfile.TemporaryDirectory() as temp:
        newpath = path.join(temp, "test-image.png")
        shutil.copy(p1, newpath)
        image1_id = upload_image(newpath)
        shutil.copy(p2, newpath)
        image2_id = upload_image(newpath)

    return image1_id, image2_id
