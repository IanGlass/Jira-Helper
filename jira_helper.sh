#!/bin/bash

# Add precommit hooks for dev
preCommit="#!/bin/bash

pycodestyle source/
RESULT=\$?
[ \$RESULT -ne 0 ] && exit 1

pycodestyle tests/
RESULT=\$?
[ \$RESULT -ne 0 ] && exit 1
exit 0"

# Check if pre-commit hooks already exists
if [ ! -f .git/hooks/pre-commit ]
then
     echo "$preCommit" > .git/hooks/pre-commit
fi

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
