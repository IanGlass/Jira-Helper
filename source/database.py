

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from datetime import datetime

DISPLAY_PERIOD = '14 days'  # This is passed directly into psql query for analytics board display


class DB():
    def __init__(self):
        try:  # Try to connect to existing db for ticket analytics
            self.con = psycopg2.connect(dbname='jira_helper', user='postgres', host='', password='')  # Connect to the db
            self.con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            self.cur = self.con.cursor()

        except:  # If this reached then db does not exist, need to create it
            self.con = psycopg2.connect(dbname='postgres', user='postgres', host='', password='')  # Connect to default postgres db first
            self.con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

            self.cur = self.con.cursor()
            self.cur.execute('CREATE DATABASE jira_helper')

            # Connect to new db
            self.con = psycopg2.connect(dbname='jira_helper', user='postgres', host='', password='')
            self.con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            self.cur = self.con.cursor()
            # Populate ticket_history with a table and cols
            self.cur.execute('''CREATE TABLE IF NOT EXISTS ticket_history(
            stamp timestamptz PRIMARY KEY,
            support int NOT NULL,
            in_progress int NOT NULL,
            customer int NOT NULL,
            dev int NOT NULL,
            design int NOT NULL,
            test int NOT NULL)''')

            # Populate settings with a table and cols
            self.cur.execute('''CREATE TABLE IF NOT EXISTS settings(
            jira_url TEXT UNIQUE,
            username TEXT UNIQUE,
            api_key TEXT UNIQUE,
            support_status TEXT UNIQUE,
            customer_status TEXT UNIQUE,
            in_progress_status TEXT UNIQUE,
            dev_status TEXT UNIQUE,
            design_status TEXT UNIQUE,
            test_status TEXT UNIQUE)''')

        # Fetch whats currently in DB and add to form on startup, all pages will use these vars
        self.settings = dict(jira_url=0, username=0, api_key=0, support_status=0, customer_status=0, in_progress_status=0, dev_status=0, design_status=0, test_status=0)
        self.fetch_settings()

    def save_ticket_history(self, support, customer, in_progress, dev, design, test):

        date = datetime.utcnow()  # Get current date in UTC to save to db

        self.cur.execute('insert into ticket_history (stamp, support, customer, in_progress, dev, design, test) values (%s, %s, %s, %s, %s, %s, %s)', (date, support, customer, in_progress, dev, design, test))

    def fetch_ticket_history(self):
        # Fetch ticket history from db, only get tickets younger than DISPLAY_PERIOD
        self.cur.execute('select stamp, support, customer, in_progress, dev, design, test from ticket_history where stamp > now() - %(period)s::interval', {"period": DISPLAY_PERIOD})
        history = self.cur.fetchall()
        return history

    def save_settings(self):
        # Delete everything in the table first
        self.cur.execute('delete from settings')
        # Add updated values to the table
        self.cur.execute('insert into settings (jira_url, username, api_key, support_status, customer_status, in_progress_status, dev_status, design_status, test_status) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)', (self.settings.get('jira_url'), self.settings.get('username'), self.settings.get('api_key'), self.settings.get('support_status'), self.settings.get('customer_status'), self.settings.get('in_progress_status'), self.settings.get('dev_status'), self.settings.get('design_status'), self.settings.get('test_status')))

    def fetch_settings(self):  # Populates global settings dictionary from db
        self.cur.execute('select jira_url, username, api_key, support_status, customer_status, in_progress_status, dev_status, design_status, test_status from settings limit 1')
        ret = self.cur.fetchall()
        try:
            self.settings = {
                "jira_url": ret[0][0],
                "username": ret[0][1],
                "api_key": ret[0][2],
                "support_status": ret[0][3],
                "customer_status": ret[0][4],
                "in_progress_status": ret[0][5],
                "dev_status": ret[0][6],
                "design_status": ret[0][7],
                "test_status": ret[0][8]
            }
        except:
            print("No saved settings")


if __name__ == 'database':
    database = DB()
