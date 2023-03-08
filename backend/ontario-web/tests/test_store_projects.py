# GNU AGPL v3 License
# Test storing projects on the server

import tempfile
import shutil
import zipfile

from os import path


def test_store_projects(client):
    # Copy the test pipeline to the server.
    with tempfile.TemporaryDirectory() as dir:
        test_path = path.join(path.dirname(__file__),
                              "assets", "test-pipeline.zip")
        target_path = path.join(dir, "test_pipeline.zip")
        shutil.copyfile(test_path, target_path)

        # First, register and then login
        username = "sammy7"
        password = "notmypassword"
        realname = "Sammy Seven"

        response = client.post(
            '/api/register',
            json=dict(
                username=username,
                password=password,
                realname=realname
            )
        )
        assert response.status_code == 200

        response = client.post(
            '/api/login',
            json=dict(
                username=username,
                password=password
            )
        )
        assert response.status_code == 200

        # Upload the project
        response = client.put(
            '/api/project/upload',
            content_type='multipart/form-data',
            data=dict(
                name="Test Pipeline",
                description="A test pipeline",
                zip=(open(target_path, 'rb'), target_path)
            )
        )
        assert response.status_code == 200

        # If we list the projects from our user, we should see the one we
        # just uploaded.
        response = client.get(f'/api/projects/{username}')
        assert response.status_code == 200

        projects = response.json
        assert len(projects) == 1
        assert projects[0]['name'] == "Test Pipeline"
        assert projects[0]['description'] == "A test pipeline"
        project_id = projects[0]['id']

        # Download the project
        response = client.get(f'/api/project/{project_id}')
        assert response.status_code == 200

        # The zip file should have the same files as the original
        with tempfile.NamedTemporaryFile(suffix=".zip") as temp:
            temp.write(response.data)
            temp.flush()

            with zipfile.ZipFile(temp.name, "r") as zip_ref:
                with zipfile.ZipFile(test_path, "r") as test_zip_ref:
                    assert zip_ref.namelist() == test_zip_ref.namelist()
