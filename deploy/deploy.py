# GNU AGPL v3 License
# Written by John Nunley

# Compiles the web frontend/backend into single files and puts them in the
# correct locations for the web server to serve them.

import os
import shutil
import subprocess as sp
import sys

from os import path

def webpackAt(p: str):
  """
  Runs webpack at the given path.
  """
  
  # Run webpack
  env = os.environ.copy()
  env["NODE_ENV"] = "development"
  res = sp.run(["npx", "webpack"], cwd=p, check=True, env=env)

  if res.returncode != 0:
    raise Exception("Webpack failed")

def copyFile(from_: str, to_: str):
  with open(from_, "rb") as f:
    with open(to_, "wb") as f2:
      f2.write(f.read()) 

def main():
  if len(sys.argv) != 2:
    print("Usage: python deploy.py <path to web root>")
    sys.exit(1)

  # Get the path to the web root
  webRoot = sys.argv[1]

  os.makedirs(webRoot, exist_ok=True)

  # Get the paths to the frontend
  frontend = path.join(path.dirname(__file__), "..", "frontend", "pictonode-web")
  backend = path.join(path.dirname(__file__), "..", "backend", "ontario-web")

  # Compile the frontend
  webpackAt(frontend)

  shutil.copytree(path.join(backend, "ontario_web"), path.join(webRoot, "ontario_web")) 

  # Make a "public" directory
  public = path.join(webRoot, "public")
  os.makedirs(public, exist_ok=True)

  # Copy the contents of "static" to the "public" directory
  static = path.join(frontend, "static")
  for f in os.listdir(static):
    shutil.copy(path.join(static, f), path.join(public, f))

  # Copy the contents of "frontend/dist" to the "public" directory
  frontendDist = path.join(frontend, "dist")
  for f in os.listdir(frontendDist):
    shutil.copy(path.join(frontendDist, f), path.join(public, f))

if __name__ == "__main__":
  main()
