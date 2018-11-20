# Creates an object containing all the methods used to interact with the database. Also contains the locally cached variables used by the program

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
            test_status TEXT UNIQUE,
            black_alert FLOAT UNIQUE,
            red_alert FLOAT UNIQUE,
            melt_down FLOAT UNIQUE)''')

        # Fetch whats currently in DB and add to form on startup, all pages will use these vars
        self.settings = dict(jira_url='', username='', api_key='', support_status='', customer_status='', in_progress_status='', dev_status='', design_status='', test_status='', black_alert=60 * 60 * 24 * 2, red_alert=60 * 60 * 24 * 7, melt_down=60 * 60 * 24 * 14)
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
        self.cur.execute('insert into settings (jira_url, username, api_key, support_status, customer_status, in_progress_status, dev_status, design_status, test_status, black_alert, red_alert, melt_down) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (self.settings['jira_url'], self.settings['username'], self.settings['api_key'], self.settings['support_status'], self.settings['customer_status'], self.settings['in_progress_status'], self.settings['dev_status'], self.settings['design_status'], self.settings['test_status'], self.settings['black_alert'], self.settings['red_alert'], self.settings['melt_down']))

    def fetch_settings(self):  # Populates global settings dictionary from db
        self.cur.execute('select jira_url, username, api_key, support_status, customer_status, in_progress_status, dev_status, design_status, test_status, black_alert, red_alert, melt_down from settings limit 1')
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
                "test_status": ret[0][8],
                "black_alert": ret[0][9],
                "red_alert": ret[0][10],
                "melt_down": ret[0][11]
            }
        except:
            print("No saved settings")


if __name__ == 'database_model':
    database_model = DB()
