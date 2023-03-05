# GNU AGPL v3 License
# Written by John Nunley

import os
import psycopg2

import click
from dotenv import load_dotenv
from flask import current_app, g
from flask.cli import with_appcontext
from os import path


def get_db() -> psycopg2.extensions.connection:
    if 'db' not in g:
        g.db = psycopg2.connect(
            dbname=current_app.config['DATABASE'],
            user=current_app.config['USER'],
            password=current_app.config['PASSWORD'],
            host=current_app.config['HOST'],
            port=current_app.config['PORT']
        )

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def env_or_else(key: str, default: str) -> str:
    if key in os.environ:
        return os.environ[key]
    else:
        return default


def init_db(test_config=None):
    load_dotenv(path.join(path.dirname(__file__), ".env"))

    def env_config_or_else(key: str, tkey: str, default: str) -> str:
        if test_config and tkey in test_config:
            return test_config[tkey]
        else:
            return env_or_else(key, default)

    # Connect to the database
    conn = psycopg2.connect(
        host=env_config_or_else("POSTGRES_HOST", "HOST", "localhost"),
        database=env_config_or_else("POSTGRES_DB", "DATABASE", "ontario"),
        user=env_config_or_else("POSTGRES_USER", "USER", "ontario"),
        password=env_config_or_else(
            "POSTGRES_PASSWORD",
            "PASSWORD",
            "ontario"
        ),
    )

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Create the users table
    cur.execute("""
    DROP TABLE IF EXISTS users;
  """)

    cur.execute("""
    CREATE TABLE users (
      id SERIAL PRIMARY KEY,
      username VARCHAR(255) UNIQUE NOT NULL,
      pwd VARCHAR(255) NOT NULL,
      realname VARCHAR(255) NOT NULL
    );
  """)

    # Create the projects table
    cur.execute("""
    DROP TABLE IF EXISTS projects;
    """)
    cur.execute("""
    CREATE TABLE projects (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        description VARCHAR(255) NOT NULL
        owner INTEGER NOT NULL,
        FOREIGN KEY (owner) REFERENCES users (id)
    );
    """)

    conn.commit()
    cur.close()
    conn.close()

    print("Database initialized successfully.")


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')
