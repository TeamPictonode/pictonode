# GNU AGPL v3 License
# Written by John Nunley

import psycopg2

from flask import current_app, g
from flask.cli import with_appcontext

def get_db() -> psycopg2.extensions.connection:
  if 'db' not in g:
    g.db = psycopg2.connect(
      dbname=current_app.config['DATABASE'],
      user=current_app.config['USER'],
      password=current_app.config['PASSWORD'],
      host=current_app.config['HOST'],
      port=current_app.config['PORT']
    )

    g.db.row_factory = psycopg2.extras.DictCursor

  return g.db

def close_db(e=None):
  db = g.pop('db', None)

  if db is not None:
    db.close()
