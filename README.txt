LoginProject README
==================

My attempt at a skeleton Pyramid-based web project.  The intent is for a basic starter project that supports a MySQL backend and has the basic setup for Pyramid's ACLs.  I also wanted support for 3rd party logins (sign in via Google, Facebook, etc.) so to not have to worry about maintaining my own passwords.

Features:

Pyramid
SQLAlchemy
pyramid_beaker for session management
authomatic for 3rd party login support
logging handlers for logging to a database, and friendly error handler templates

Getting Started
---------------

- cd <directory containing this file>

- $venv/bin/python setup.py develop

- $venv/bin/initialize_LoginProject_db development.ini

- $venv/bin/pserve development.ini

