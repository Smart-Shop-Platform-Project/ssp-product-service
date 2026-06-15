from motor.motor_asyncio import AsyncIOMotorClient
import boto3
import logging
from .config import settings
import os

logger = logging.getLogger("ssp-product-service")

class Database:
    client: AsyncIOMotorClient = None

db = Database()

def get_ssm_parameter(name):
    try:
        ssm_client = boto3.client('ssm', region_name=settings.AWS_REGION)
        parameter = ssm_client.get_parameter(Name=name, WithDecryption=True)
        return parameter['Parameter']['Value']
    except Exception as e:
        logger.critical(f"Error fetching parameter {name}: {e}")
        raise

async def connect_to_mongo():
    logger.info("Connecting to MongoDB...")
    try:
        mongo_uri = get_ssm_parameter(settings.MONGO_URI_PARAM_NAME)
    except Exception as e:
        logger.error(f"Could not load MONGO_URI from SSM, falling back to localhost: {e}")
        mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017")

    db.client = AsyncIOMotorClient(mongo_uri)
    logger.info("Connected to MongoDB.")

async def close_mongo_connection():
    logger.info("Closing MongoDB connection...")
    if db.client:
        db.client.close()
        logger.info("MongoDB connection closed.")
