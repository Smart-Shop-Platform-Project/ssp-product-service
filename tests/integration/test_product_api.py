import pytest
from unittest.mock import patch, AsyncMock
import json

def test_get_products_api(client):
    # Mock the service layer to isolate the API from the database
    mock_products = [
        {"id": "1", "name": "Laptop", "description": "A good laptop", "mrp": 1200.0, "discount_percent": 10.0, "selling_price": 1080.0, "category": "Electronics", "image_url": None},
        {"id": "2", "name": "Mouse", "description": "A good mouse", "mrp": 25.0, "discount_percent": 0, "selling_price": 25.0, "category": "Electronics", "image_url": None}
    ]
    with patch("app.api.product_routes.product_service.get_all_products", new_callable=AsyncMock) as mock_get_all:
        mock_get_all.return_value = mock_products
        
        response = client.get("/api/v1/products")
        
        assert response.status_code == 200
        assert response.json() == mock_products
        mock_get_all.assert_called_once()

def test_get_single_product_api_found(client):
    mock_product = {"id": "1", "name": "Laptop", "description": "A good laptop", "mrp": 1200.0, "discount_percent": 10.0, "selling_price": 1080.0, "category": "Electronics", "image_url": None}
    with patch("app.api.product_routes.product_service.get_product_by_id", new_callable=AsyncMock) as mock_get_one:
        mock_get_one.return_value = mock_product
        
        response = client.get("/api/v1/products/1")
        
        assert response.status_code == 200
        assert response.json() == mock_product
        mock_get_one.assert_called_once_with("1")

def test_get_single_product_api_not_found(client):
    with patch("app.api.product_routes.product_service.get_product_by_id", new_callable=AsyncMock) as mock_get_one:
        # Simulate the service raising the correct exception
        from fastapi import HTTPException
        mock_get_one.side_effect = HTTPException(status_code=404, detail="Product not found")
        
        response = client.get("/api/v1/products/999")
        
        assert response.status_code == 404
        assert response.json() == {"detail": "Product not found"}

def test_create_product_api(client):
    product_data = {"id": "new_prod", "name": "New Keyboard", "mrp": 75.0, "category": "Electronics"}
    
    # We need to mock the service layer's create_product method
    with patch("app.api.product_routes.product_service.create_product", new_callable=AsyncMock) as mock_create:
        # The service layer is responsible for calculating selling_price and handling image URL
        mock_create.return_value = {**product_data, "selling_price": 75.0, "image_url": None}
        
        # When sending multipart/form-data, data must be in a 'files' dictionary
        # The product_data needs to be a JSON string
        files = {'product_data': (None, json.dumps(product_data), 'application/json')}
        
        response = client.post("/api/v1/products", files=files)
        
        assert response.status_code == 200
        assert response.json()["id"] == "new_prod"
        assert response.json()["selling_price"] == 75.0
        mock_create.assert_called_once()
