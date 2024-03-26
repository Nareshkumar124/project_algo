from pymongo import MongoClient
from ..constant import DB_NAME
from os import getenv


try: 
    client=MongoClient(getenv("DB_URL"))
    print("database connented")
except Exception as e:
    print(e)
    exit(0)

db=client[DB_NAME]

userCollection=db["users"]
videoCollection=db["videos"]