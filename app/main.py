from fastapi import FastAPI
import logging
import sys
from .core.database import connect_to_mongo, close_mongo_connection
from .api.product_routes import router as product_router
from .repositories.product_repository import ProductRepository

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='{"time":"%(asctime)s", "level":"%(levelname)s", "message":"%(message)s"}',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("ssp-product-service")

app = FastAPI(title="SSP Product Service")

@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()
    # Initialize indexes on startup
    repo = ProductRepository()
    await repo.initialize_indexes()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

# Include the routers
app.include_router(product_router, prefix="/api/v1")

@app.get("/", tags=["Health Check"])
async def root():
    return {"message": "SSP Product Service is running"}
