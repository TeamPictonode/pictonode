#!/bin/bash
# GNU AGPL v3 License
# Written by John Nunley

# Runs pytest in the root of all of the Python projects in the repo
set -ex
PY_PROJECTS=(
  "backend/ontario"
  "backend/ontario-web"
)

# Make sure pytest is installed
if ! command -v pytest &> /dev/null
then
  echo "pytest could not be found. Please install it with 'pip install pytest'"
  exit
fi

for project in "${PY_PROJECTS[@]}"
do
  echo "Running pytest on $project"
  pushd $project
  pytest
  popd
done
