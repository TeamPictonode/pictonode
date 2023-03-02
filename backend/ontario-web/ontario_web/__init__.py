# GNU AGPLv3 License
# Written by John Nunley

import os
from os import path as os_path
import tempfile
import psycopg2

from . import db
from . import image_manager
from . import processor

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
        PORT=env_or_else("POSTGRES_PORT", "5432")
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

    app.teardown_appcontext(db.close_db)

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

    return app
