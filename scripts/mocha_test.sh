#!/bin/bash
# GNU AGPL v3 License
# Written by John Nunley

# Runs unit tests for the JavaScript projects in the repo
set -ex

JS_PROJECTS=(
  "libraries/libnode"
  "frontend/pictonode-web"
)

# Make sure mocha is installed
if ! command -v npx mocha &> /dev/null
then
  echo "Mocha could not be found. Please install it with 'npm install'"
  exit
fi

export TS_NODE_COMPILER_OPTIONS='{"module":"commonjs"}'

for project in "${JS_PROJECTS[@]}"
do
  echo "Running mocha on $project"
  pushd $project
  # Run mocha for all files in tests/**/*.ts
  npx mocha --recursive --require ts-node/register tests/**/*.ts
  popd
done

