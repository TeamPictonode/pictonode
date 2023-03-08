#!/bin/bash
# GNU AGPL v3 License
# Written by John Nunley

# Runs prettier on all JS projects in the repo and runs autopep8 on all Python projects in the repo
# Run this script from the root of the repo

# Exit if any command fails and print each command before running it
set -ex

# Run prettier on all JS projects
JS_PROJECTS=(
  "libraries/libnode"
  "frontend/pictonode-web"
)

# Make sure prettier is installed
if ! command -v npx prettier &> /dev/null
then
  echo "Prettier could not be found. Please install it with 'npm install'"
  exit
fi

for project in "${JS_PROJECTS[@]}"
do
  echo "Running prettier on $project"
  npx prettier --write $project
done

# Run autopep8 on all Python projects
PY_PROJECTS=(
  "gimp/gtk-nodes-init"
  "gimp/pictonode-gimp-plugin/.gimpfiles"
  "backend/ontario"
  "backend/ontario-web"
)

# Make sure autopep8 is installed
if ! command -v autopep8 &> /dev/null
then
  echo "autopep8 could not be found. Please install it with 'pip install autopep8'"
  exit
fi

for project in "${PY_PROJECTS[@]}"
do
  echo "Running autopep8 on $project"
  # List all .py files in the project and run autopep8 on them
  for file in $(find $project -name "*.py")
  do
    autopep8 --in-place "$file"
  done
done

