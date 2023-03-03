# GNU AGPL v3 License
# Written by John Nunley

# Creates the "public" directory if it doesn't exist

import os
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
    sp.run(["npm", "install"], cwd=p, check=True, env=env)
    res = sp.run(["npx", "webpack"], cwd=p, check=True, env=env)

    if res.returncode != 0:
        raise Exception("Webpack failed")


def copyFile(from_: str, to_: str):
    with open(from_, "rb") as f:
        with open(to_, "wb") as f2:
            f2.write(f.read())


def main():
    if len(sys.argv) != 2:
        public_dir = path.join(path.dirname(__file__), "public")
    else:
        public_dir = sys.argv[1]

    os.makedirs(public_dir, exist_ok=True)

    # Get the paths to the frontend
    frontend = path.join(
        path.dirname(__file__),
        "..",
        "..",
        "frontend",
        "pictonode-web"
    )

    # Compile the frontend
    webpackAt(frontend)

    # Copy the contents of "frontend/dist" and "frontend/static" to
    # the "public" directory
    for f in os.listdir(path.join(frontend, "dist")):
        copyFile(
            path.join(frontend, "dist", f),
            path.join(public_dir, f)
        )

    for f in os.listdir(path.join(frontend, "static")):
        copyFile(
            path.join(frontend, "static", f),
            path.join(public_dir, f)
        )


if __name__ == "__main__":
    main()
