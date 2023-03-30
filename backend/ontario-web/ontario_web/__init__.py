# GNU AGPLv3 License
# Written by John Nunley

import os
from os import path as os_path
import tempfile
import psycopg2

from . import db
from . import image_manager
from . import processor
from . import save_and_load

from flask import Flask, request, send_file, session
from werkzeug.security import check_password_hash, generate_password_hash

import atexit
import random

from dotenv import load_dotenv

from apscheduler.schedulers.background import BackgroundScheduler


def env_or_else(key: str, default: str) -> str:
    if key in os.environ:
        return os.environ[key]
    else:
        return default


def create_app(test_config=None):
    load_dotenv(os_path.join(os_path.dirname(__file__), ".env"))

    # Public directory
    public_dir = os_path.join(os_path.dirname(__file__), "..", "public")

    # Create and configure the app
    app = Flask(
        __name__,
        instance_relative_config=True,
        static_folder=public_dir)
    app.config.from_mapping(
        SECRET_KEY=os.urandom(16),
        DATABASE=env_or_else("POSTGRES_DB", "ontario_db"),
        USER=env_or_else("POSTGRES_USER", "ontario"),
        PASSWORD=env_or_else("POSTGRES_PASSWORD", "ontario"),
        HOST=env_or_else("POSTGRES_HOST", "localhost"),
        PORT=env_or_else("POSTGRES_PORT", "5432"),
        INSTANCE_PATH=os_path.join(app.root_path, "instance"),
    )

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Host all files in the "public" folder
    @app.route("/<path:path>")
    def host_file(path):
        return app.send_static_file(path)

    # Root goes to index.html
    @app.route("/")
    def index():
        return app.send_static_file("index.html")

    # Set up a task scheduler
    scheduler = BackgroundScheduler()
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())
    app.extensions["scheduler"] = scheduler

    # Register the image image manager to clean up every 2 hours
    im = image_manager.ImageManager("/tmp/ontario", 1024 * 1024 * 1024, "webp")
    scheduler.add_job(
        func=im.clean_up,
        trigger="interval",
        hours=2,
        id="image_manager_clean_up",
    )

    # Create a directory to store projects in
    instance_path = app.config["INSTANCE_PATH"]
    if not os_path.exists(instance_path):
        os.makedirs(instance_path)
    projects_path = os_path.join(instance_path, "projects")
    if not os_path.exists(projects_path):
        os.makedirs(projects_path)

    app.teardown_appcontext(db.close_db)
    app.cli.add_command(db.init_db_command)

    # For /api/upload_image, save an image to a file and then save it
    # to the database
    @app.route("/api/upload_image", methods=["POST"])
    def upload_image():
        # The body of the request should be an image
        image = request.files["image"]

        # Save the image to the disk
        with tempfile.TemporaryDirectory() as dir:
            ext = os_path.splitext(image.filename)[1]
            p = os_path.join(dir, f"image.{ext}")
            with open(p, "wb") as file:
                file.write(image.read())
            new_id = im.add_image(p)
            return {"id": new_id}

    # For /api/process, take the body of the request and process it
    # as a JSON pipeline, using the "processor" module
    @app.route("/api/process", methods=["POST"])
    def process():
        # The body of the request should be a JSON pipeline
        pipeline = request.get_json()
        print("PIPELINE: ")
        print(pipeline)
        id = random.randint(0, 1000000000)
        filename = f"/tmp/ontario/out{id}.webp"
        processor.process(pipeline, im, filename)
        print(filename)

        # The body of the response should be the output image
        return send_file(filename)

    # For /api/register, take the username, realname and password
    # from the body of the request and save them to the database
    # Make sure to hash the password
    @app.route("/api/register", methods=["POST"])
    def register():
        # The body of the request should be a JSON object with the
        # username, realname and password
        user = request.get_json()
        username = user["username"]
        realname = user["realname"]
        password = user["password"]

        error = None

        if not username:
            error = "Username is required."
        elif not realname:
            error = "Real name is required."
        elif not password:
            error = "Password is required."

        # Make sure the username is not already taken
        if not error:
            d = db.get_db()
            cursor = d.cursor()
            try:
                cursor.execute(
                    """
                    INSERT INTO users (username, realname, pwd)
                    VALUES (%s, %s, %s)
                    """,
                    (username, realname, generate_password_hash(password)),
                )
                d.commit()
            except psycopg2.IntegrityError:
                error = f"User {username} is already registered."
            finally:
                cursor.close()

        if error:
            return {"error": error}, 400
        else:
            return {"success": True}

    # For /api/login, take the username and password from the body
    # of the request and check them against the database
    # Make sure to hash the password
    @app.route("/api/login", methods=["POST"])
    def login():
        # The body of the request should be a JSON object with the
        # username and password
        user = request.get_json()
        username = user["username"]
        password = user["password"]

        error = None

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."

        if not error:
            d = db.get_db()
            cursor = d.cursor()
            user = None
            try:
                cursor.execute(
                    "SELECT * FROM users WHERE username = %s", (username,)
                )
                user = cursor.fetchone()
            except psycopg2.OperationalError:
                error = "Incorrect username."

            if user is None:
                error = "Incorrect username."
            elif not check_password_hash(user[2], password):
                error = "Incorrect password."

        if error:
            return {"error": error}, 400
        else:
            session.clear()
            session["user_id"] = user[0]
            return {"success": True}

    # For /api/save, take a JSON pipeline and return a saved .zip file
    # containing the pipeline and the necessary images
    @app.route("/api/save", methods=["POST"])
    def save():
        # The body of the request should be a JSON object with the
        # pipeline
        pipeline = request.get_json()

        # Create a temporary directory
        with tempfile.TemporaryDirectory() as dir:
            save_path = os_path.join(dir, "pipeline.zip")
            save_and_load.save_to_zip(
                im,
                pipeline,
                save_path
            )

            # The body of the response should be the .zip file
            return send_file(save_path)

    # For /api/load, take a .zip file and return a JSON pipeline
    @app.route("/api/load", methods=["POST"])
    def load():
        # The body of the request should be a .zip file
        file = request.files["file"]

        # Create a temporary directory
        with tempfile.TemporaryDirectory() as dir:
            save_path = os_path.join(dir, "pipeline.zip")
            file.save(save_path)

            # The body of the response should be the JSON pipeline
            return save_and_load.load_from_zip(im, save_path)

    # For /api/projects, return a list of all projects associated with
    # the username
    @app.route("/api/projects/<username>", methods=["GET"])
    def projects(username):
        d = db.get_db()
        cursor = d.cursor()
        projects = []
        try:
            # Select id, name, description from projects, where the
            # owner id is the user with the given username
            cursor.execute(
                """
                SELECT p.id, p.name, p.description
                FROM projects p
                INNER JOIN users u
                ON p.owner = u.id
                WHERE u.username = %s
                """,
                (username,),
            )
            projects = cursor.fetchall()
        except psycopg2.OperationalError:
            pass
        finally:
            cursor.close()

        ret_projects = []
        for project in projects:
            ret_projects.append(
                {
                    "id": project[0],
                    "name": project[1],
                    "description": project[2],
                }
            )

        return ret_projects

    def _check_project_exists(id):
        d = db.get_db()
        cursor = d.cursor()
        project = None
        try:
            # Make sure the project exists
            cursor.execute(
                """
                SELECT * FROM projects
                WHERE id = %s
                """,
                (id,),
            )
            project = cursor.fetchone()
        except psycopg2.OperationalError:
            pass
        finally:
            cursor.close()

        return project is not None

    # For /api/project/id, return the project ZIP with the given id
    @app.route("/api/project/<id>", methods=["GET"])
    def project_json(id):
        if not _check_project_exists(id):
            return {"error": "Project does not exist."}, 404

        # The project JSON is at the projects dir, at file
        p = os_path.join(projects_path, f"project{id}.zip")

        # Send the file over
        return send_file(p)

    # Upload a JSON and an XCF file to the projects dir
    @app.route("/api/project/upload", methods=["PUT"])
    def project_upload():
        # Request is form data that contains:
        # - name
        # - description
        # - zip
        name = request.form["name"]
        description = request.form["description"]
        zip = request.files["zip"]

        # Make sure the user is logged in
        if "user_id" not in session:
            return {"error": "Not logged in."}, 401

        # Insert into the projects table
        d = db.get_db()
        cursor = d.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO projects (name, description, owner)
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (name, description, session["user_id"]),
            )
            id = cursor.fetchone()[0]
            d.commit()
        except psycopg2.OperationalError:
            return {"error": "Error uploading project."}, 500
        finally:
            cursor.close()

        # Save the file
        zip.save(os_path.join(projects_path, f"project{id}.zip"))

        # Return the id of the project
        return {"id": id}

    # Upload a JSON and XCF file to an existing project.
    # The project id is in the URL
    @app.route("/api/project/upload/<id>", methods=["POST"])
    def project_upload_existing(id):
        # Request contains:
        # - ZIP file
        zip = request.files["zip"]

        # Make sure the user is logged in
        if "user_id" not in session:
            return {"error": "Not logged in."}, 401

        # Make sure the project exists
        if not _check_project_exists(id):
            return {"error": "Project does not exist."}, 404

        # Save the zip file
        zip.save(os_path.join(projects_path, f"project{id}.zip"))

        return {"success": True}

    # List all users and their realnames
    @app.route("/api/users", methods=["GET"])
    def users():
        d = db.get_db()
        cursor = d.cursor()
        users = []
        try:
            cursor.execute(
                """
                SELECT username, realname
                FROM users
                """
            )
            users = cursor.fetchall()
        except psycopg2.OperationalError:
            pass
        finally:
            cursor.close()

        realUsers = []
        for user in users:
            realUsers.append(
                {
                    "username": user[0],
                    "realname": user[1],
                }
            )

        return realUsers

    return app
