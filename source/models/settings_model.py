
import sqlite3
from sqlalchemy import Column, Float, String, Integer, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import validates

Base = declarative_base()


class SettingsModel(Base):
    __tablename__ = 'settings'
    ID = Column(Integer, primary_key=True)
    jira_url = Column(String)
    username = Column(String)
    api_key = Column(String)
    support_status = Column(String)
    customer_status = Column(String)
    in_progress_status = Column(String)
    dev_status = Column(String)
    design_status = Column(String)
    test_status = Column(String)
    black_alert = Column(Float)
    red_alert = Column(Float)
    melt_down = Column(Float)
    clean_queue_delay = Column(Float)
    automated_message = Column(String)


# Create an engine that stores data in the local directory's jira_helper.sql file
engine = create_engine('sqlite:///jira_helper.db')
# Create all tables in the engine
Base.metadata.create_all(engine)
