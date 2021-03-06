import sqlalchemy
from sqlalchemy import create_engine, MetaData
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd


def getEngine(connection_data):
    if connection_data[0] == "PG":
        # print(connection_data)
        connection_string = f'postgresql+psycopg2://{connection_data[1]}:{connection_data[2]}@{connection_data[3]}:{connection_data[-1]}/{connection_data[4]}'
        # print("GetEngine: " + connection_string)
    else:
        pass
    return connection_string


def testConnection(connection_data):
    # print("testConnection: " + str(connection_data))
    connection_string = getEngine(connection_data)
    # print("testConnection: " + connection_string)
    try:
        alchemyEngine = create_engine(connection_string, pool_recycle=3600)
        dbConnection = alchemyEngine.connect()
        dbConnection.close()
        return True
    except:
        return False


def sensitiveCensor(df):
    import hashlib
    df_hashed = pd.DataFrame()
    for column in df:
        df[column] = df[column].astype(str)
        df_hashed[column] = df[column].apply(
            lambda x:
            hashlib.md5(x.encode()).hexdigest()
        )
    return df_hashed
