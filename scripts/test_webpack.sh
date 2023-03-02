#!/bin/bash
# GNU AGPL v3 License
# Written by John Nunley

# Runs webpack on the web frontend to make sure it still builds

set -ex
pushd frontend/pictonode-web
npx webpack
popd
