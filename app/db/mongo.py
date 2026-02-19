# MongoDB connection logic
from pymongo import MongoClient
from langgraph.checkpoint.mongodb import MongoDBSaver

client = MongoClient("mongodb://localhost:27017")
checkpointer = MongoDBSaver(client)