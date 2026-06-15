import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.product_service import ProductService
from app.models.product import Product
from fastapi import HTTPException
from fastapi import UploadFile
import io

@pytest.fixture
def mock_repository():
    return AsyncMock()

@pytest.fixture
def product_service(mock_repository):
    service = ProductService()
    service.repository = mock_repository
    return service

@pytest.mark.asyncio
async def test_get_all_products(product_service, mock_repository):
    expected_products = [
        Product(id="1", name="Product A", price=100.0, category="Test", mrp=120.0, selling_price=100.0),
        Product(id="2", name="Product B", price=200.0, category="Test", mrp=250.0, selling_price=200.0)
    ]
    mock_repository.get_all_products.return_value = expected_products

    result = await product_service.get_all_products()

    assert result == expected_products
    mock_repository.get_all_products.assert_called_once()

@pytest.mark.asyncio
async def test_get_product_by_id_success(product_service, mock_repository):
    expected_product = Product(id="1", name="Product A", price=100.0, category="Test", mrp=120.0, selling_price=100.0)
    mock_repository.get_product_by_id.return_value = expected_product

    result = await product_service.get_product_by_id("1")

    assert result == expected_product
    mock_repository.get_product_by_id.assert_called_once_with("1")

@pytest.mark.asyncio
async def test_get_product_by_id_not_found(product_service, mock_repository):
    mock_repository.get_product_by_id.return_value = None

    with pytest.raises(HTTPException) as excinfo:
        await product_service.get_product_by_id("999")
    
    assert excinfo.value.status_code == 404

@pytest.mark.asyncio
async def test_create_product_success(product_service, mock_repository):
    new_product = Product(id="new1", name="New Product", price=50.0, category="Test", mrp=50.0, selling_price=50.0)
    mock_repository.get_product_by_id.return_value = None
    mock_repository.create_product.return_value = new_product

    result = await product_service.create_product(new_product)

    assert result == new_product
    mock_repository.create_product.assert_called_once()

@pytest.mark.asyncio
async def test_create_product_duplicate(product_service, mock_repository):
    existing_product = Product(id="existing1", name="Existing", price=50.0, category="Test", mrp=50.0, selling_price=50.0)
    mock_repository.get_product_by_id.return_value = existing_product

    with pytest.raises(HTTPException) as excinfo:
        await product_service.create_product(existing_product)
    
    assert excinfo.value.status_code == 400

@pytest.mark.asyncio
async def test_create_product_with_image(product_service, mock_repository):
    new_product = Product(id="new_img", name="Image Product", price=50.0, category="Test", mrp=50.0, selling_price=50.0)
    mock_repository.get_product_by_id.return_value = None
    
    # Mock the internal S3 upload method to avoid AWS calls
    with patch.object(product_service, '_upload_image_to_s3', return_value="https://s3.amazonaws.com/bucket/img.jpg"):
        mock_repository.create_product.side_effect = lambda p: p # just return the passed product

        file_obj = io.BytesIO(b"dummy image data")
        upload_file = UploadFile(filename="test.jpg", file=file_obj, content_type="image/jpeg")
        
        result = await product_service.create_product(new_product, image=upload_file)

        assert result.image_url == "https://s3.amazonaws.com/bucket/img.jpg"
        mock_repository.create_product.assert_called_once()
