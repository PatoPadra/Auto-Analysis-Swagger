import pandas as pd
from sqlalchemy import create_engine

def fetch_data_from_sql(server, database, table):
    SERVER_NAME = server
    PORT = ''
    DATABASE_NAME = database
    USERNAME = ''
    PASSWORD = ''

    # Construct the connection string using SQLAlchemy's create_engine
    connection_string = (
        f"mssql+pyodbc://{USERNAME}:{PASSWORD}@{SERVER_NAME}:{PORT}/{DATABASE_NAME}"
        f"?driver=ODBC+Driver+17+for+SQL+Server"
    )

    # Create a SQLAlchemy engine
    engine = create_engine(connection_string)

    # Fetch data from the database
    query = f"SELECT  * FROM {table}"
    df = pd.read_sql(query, engine)

    return df,table
