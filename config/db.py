from pymongo import MongoClient
from os import environ
import urllib.parse

# prefix = 'mongodb+srv://'
#
# user = urllib.parse.quote(str(environ['MONGODB_PASSWORD']))
#
# suffix = '@learningcluster.yl2l9ok.mongodb.net/?retryWrites=true&w=majority'
#
# conn = MongoClient(prefix + user + suffix)

# print(urllib.parse.quote(environ['MONGODB_PASSWORD']))
conn = MongoClient("mongodb+srv://learningmongo:" + urllib.parse.quote(environ['MONGODB_PASSWORD']) + "@learningcluster.yl2l9ok.mongodb.net/?retryWrites=true&w=majority")


