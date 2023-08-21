from pymongo import MongoClient
from pymongo.errors import PyMongoError
from os import environ
import urllib.parse

def validate_db():
    conn = MongoClient("mongodb+srv://learningmongo:" + urllib.parse.quote(environ['MONGODB_PASSWORD']) + "@learningcluster.yl2l9ok.mongodb.net/?retryWrites=true&w=majority")
    return conn