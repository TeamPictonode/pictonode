# GNU AGPLv3 License
# Written by John Nunley

import os

from flask import Flask

def create_app(test_config = None):
  # Create and configure the app
  app = Flask(__name__, instance_relative_config = True)
  app.config.from_mapping(
    SECRET_KEY="ontario",
    # TODO: not sqlite
    DATABASE=os.path.join(app.instance_path, "ontario.sqlite"),
  )

  if test_config is None:
    # Load the instance config, if it exists, when not testing
    app.config.from_pyfile("config.py", silent = True)
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
  def send_file(path):
    return app.send_static_file(path)
  
  return app
