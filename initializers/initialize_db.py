import os
from pymongo import MongoClient

def initialize_db():
    connection_string=os.getenv('CONNECTION_STRING')
    client=MongoClient(connection_string)
    database=client.orbitos
    return database


