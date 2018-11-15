#!/bin/bash

#Install latest version of pip package manager
python -m pip install --upgrade pip

#Install PyQt5 required to run program
pip install PyQt5

#Install JIRA API for Python
pip install jira

#Install for postgresql
pip install psycopg2

#Install linter used when modifying code
pip install pycodestyle

#install matplotlib required to plot in analytics board
python -m pip install -U matplotlib

python source/main.py
