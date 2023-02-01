# GNU AGPL v3 License
# Written by John Nunley

from setup_gtknodes import setup_gtknodes
import tempfile
import os

from os import path


def runTest(target_dir):
    # Build GtkNodes.
    setup_gtknodes(target_dir)

    # Set the GI_TYPELIB_PATH to our typelib directory
    os.environ["GI_TYPELIB_PATH"] = path.join(target_dir, "introspection")

    # Set the LD_LIBRARY_PATH to our typelib directory
    os.environ["LD_LIBRARY_PATH"] = path.join(target_dir, "libs")

    # Try to import GtkNodes
    import gi
    gi.require_version("Gtk", "3.0")
    gi.require_version("GtkNodes", "0.1")


def main():
  with tempfile.TemporaryDirectory() as target_dir:
    runTest(target_dir)


if __name__ == "__main__":
  main()
