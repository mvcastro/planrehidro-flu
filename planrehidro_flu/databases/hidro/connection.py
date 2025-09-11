import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import Session

load_dotenv()

connection_string = os.getenv('DATABASE_URL', default='')
connection_url = URL.create('mssql+pyodbc', query={'odbc_connect': connection_string})
engine = create_engine(connection_url)


def get_session():
    with Session(engine) as session:
        yield session
