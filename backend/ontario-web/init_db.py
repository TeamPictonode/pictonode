# GNU AGPL v3 License
# Written by John Nunley
# DB Initialization Script for ontario-web

import os
import psycopg2

from dotenv import load_dotenv
from os import path

def env_or_else(key: str, default: str) -> str:
  if key in os.environ:
    return os.environ[key]
  else:
    return default

def main():
  load_dotenv(path.join(path.dirname(__file__), ".env"))

  # Connect to the database
  conn = psycopg2.connect(
    host = env_or_else("POSTGRES_HOST", "localhost"),
    database = env_or_else("POSTGRES_DB", "ontario"),
    user = env_or_else("POSTGRES_USER", "ontario"),
    password = env_or_else("POSTGRES_PASSWORD", "ontario"),
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
      password VARCHAR(255) NOT NULL
    );
  """)

  conn.commit()
  cur.close()
  conn.close()

  print("Database initialized successfully.")

if __name__ == "__main__":
  main()

