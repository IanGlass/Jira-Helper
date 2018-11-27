#!/bin/bash

# Install latest version of pip package manager
python -m pip install -U pip

# Install PyQt5 required to run program
pip install PyQt5

# Install JIRA API for Python
pip install jira

# Install linter used when modifying code
pip install pycodestyle

# Install matplotlib required to plot in analytics board
python -m pip install -U matplotlib

# Install database conncetor for postgresql
pip install psycopg2

# Install SQLAlchemy ORM for python and psycopg
pip install SQLAlchemy

pip install pysqlite3

python source/controllers/main_controller.py
