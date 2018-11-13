

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from datetime import datetime

DISPLAY_PERIOD = '14 days'  # This is passed directly into psql query for analytics board display


class DB():
    def __init__(self):
        try:  # Try to connect to existing db for ticket analytics
            self.con = psycopg2.connect(dbname='ticketdb', user='postgres', host='', password='')  # Connect to the db
            self.con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            self.cur = self.con.cursor()

        except:  # If this reached then db does not exist, need to create it
            self.con = psycopg2.connect(dbname='postgres', user='postgres', host='', password='')  # Connect to default postgres db first
            self.con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

            self.cur = self.con.cursor()
            self.cur.execute('CREATE DATABASE ticketdb')

            # Connect to new db
            self.con = psycopg2.connect(dbname='ticketdb', user='postgres', host='', password='')
            self.con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            self.cur = self.con.cursor()
            # Populate db with a table and cols
            self.cur.execute('''CREATE TABLE IF NOT EXISTS ticket_stats(
            stamp timestamptz PRIMARY KEY,
            support int NOT NULL,
            in_progress int NOT NULL,
            customer int NOT NULL,
            dev int NOT NULL,
            design int NOT NULL,
            test int NOT NULL)''')

    def save_ticket_history(self, support, customer, in_progress, dev, design, test):

        date = datetime.utcnow()  # Get current date in UTC to save to db

        self.cur.execute('insert into ticket_stats (stamp, support, customer, in_progress, dev, design, test) values (%s, %s, %s, %s, %s, %s, %s)', (date, support, customer, in_progress, dev, design, test))

    def fetch_ticket_history(self):
        # Fetch ticket history from db, only get tickets younger than DISPLAY_PERIOD
        self.cur.execute('select stamp, support, customer, in_progress, dev, design, test from ticket_stats where stamp > now() - %(period)s::interval', {"period": DISPLAY_PERIOD})
        history = self.cur.fetchall()
        return history


if __name__ == 'database':
    database = DB()
