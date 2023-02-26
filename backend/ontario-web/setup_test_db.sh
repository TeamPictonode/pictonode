#!/bin/sh

# GNU AGPL v3 or later
# Written by John Nunley

# This script is used to setup the test database for the ontario-web
# backend.  It is intended to be run from the root of the ontario-web
# project. It should be run as root.

# Use psql to create the test database and the test user
psql -c "CREATE DATABASE ontario_test;" -U postgres
psql -c "CREATE USER ontario_test WITH LOGIN SUPERUSER PASSWORD 'ontario_test';" -U postgres
