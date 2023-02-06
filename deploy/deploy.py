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
  env["NODE_ENV"] = "production"
  res = sp.run(["npx", "webpack"], cwd=p, check=True, env=env)

  if res.returncode != 0:
    raise Exception("Webpack failed")  

def main():
  if len(sys.argv) != 2:
    print("Usage: python deploy.py <path to web root>")
    sys.exit(1)

  # Get the path to the web root
  webRoot = sys.argv[1]

  os.makedirs(webRoot, exist_ok=True)

  # Get the paths to the frontend and backend
  frontend = path.join(path.dirname(__file__), "..", "frontend", "pictonode-web")
  backend = path.join(path.dirname(__file__), "..", "backend", "web-backend")

  # Compile the frontend and backend
  webpackAt(frontend)
  webpackAt(backend)

  # Open "backend.js" in the web root
  backendJs = path.join(webRoot, "backend.js")
  with open(backendJs, "w") as f:
    # Import the external libraries
    EXTERNALS = [
      "sharp",
      "express",
      "pg",
      "fs",
      "path",
      "os"
    ]

    for e in EXTERNALS:
      f.write(f"var {e} = require('{e}');\n")
    
    # Write the entire backend
    with open(path.join(backend, "dist", "index.js"), "r") as f2:
      f.write(f2.read())

  # Copy out deployed.json package and install all dependencies
  scriptDir = path.dirname(__file__)
  shutil.copy(path.join(scriptDir, "deployed.json"), path.join(webRoot, "package.json"))
  shutil.copy(path.join(scriptDir, ".env"), path.join(webRoot, ".env"))
  res = sp.run(["npm", "install", "--production"], cwd=webRoot, check=True)
  if res.returncode != 0:
    raise Exception("Failed to install dependencies")

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
