from motor.motor_asyncio import AsyncIOMotorClient
import os

db = AsyncIOMotorClient(os.getenv("mongodb+srv://fighterlitboy_db_user:<db_password>@cluster0.es1n0kv.mongodb.net/?appName=Cluster0")).musicbot
