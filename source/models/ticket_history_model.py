
import sqlite3
from sqlalchemy import Column, Integer, create_engine, DATETIME
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import validates

Base = declarative_base()


class TicketHistoryModel(Base):
    __tablename__ = 'ticket_history'
    stamp = Column(DATETIME, primary_key=True)
    support = Column(Integer)
    in_progress = Column(Integer)
    customer = Column(Integer)
    dev = Column(Integer)
    design = Column(Integer)
    test = Column(Integer)


# Create an engine that stores data in the local directory's jira_helper.sql file
engine = create_engine('sqlite:///jira_helper.db')
# Create all tables in the engine
Base.metadata.create_all(engine)
