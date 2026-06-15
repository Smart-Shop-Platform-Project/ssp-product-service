import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from app.main import app
from app.core.database import db as mongo_db_client # Alias to avoid conflict with fixture name

@pytest.fixture(scope="module")
def client():
    """Provides a TestClient for the FastAPI app."""
    return TestClient(app)

@pytest.fixture(scope="function")
async def mock_mongo_collection():
    """Mocks the MongoDB collection for isolated testing."""
    with patch("app.core.database.AsyncIOMotorClient") as MockMotorClient:
        mock_collection = AsyncMock()
        mock_db = AsyncMock()
        mock_db.products.products = mock_collection # Simulate db.products.products access
        MockMotorClient.return_value.__getitem__.return_value = mock_db # Simulate client.ssp_products
        
        # Ensure the global db.client is also mocked
        original_client = mongo_db_client.client
        mongo_db_client.client = MockMotorClient.return_value
        
        yield mock_collection
        
        # Restore original client after test
        mongo_db_client.client = original_client

@pytest.fixture(scope="function")
def mock_s3_client():
    """Mocks the boto3 S3 client for isolated testing."""
    with patch("boto3.client") as mock_boto_client:
        mock_s3 = AsyncMock()
        mock_boto_client.return_value = mock_s3
        yield mock_s3
