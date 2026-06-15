from fastapi import APIRouter, UploadFile, File, Form, Depends
from typing import List
from ..models.product import Product
from ..services.product_service import ProductService
import json

router = APIRouter()
product_service = ProductService()

@router.get("/products", response_model=List[Product], tags=["Products"])
async def get_products():
    return await product_service.get_all_products()

@router.get("/products/{product_id}", response_model=Product, tags=["Products"])
async def get_product(product_id: str):
    return await product_service.get_product_by_id(product_id)

# This endpoint now accepts multipart/form-data
@router.post("/products", response_model=Product, tags=["Products"])
async def create_product(
    product_data: str = Form(...),
    image: Optional[UploadFile] = File(None)
):
    # Pydantic doesn't natively handle form-data with JSON, so we parse it manually
    product_dict = json.loads(product_data)
    product = Product(**product_dict)
    return await product_service.create_product(product, image)

# You would also add PUT/PATCH endpoints for updating products
@router.put("/products/{product_id}", response_model=Product, tags=["Products"])
async def update_product(
    product_id: str,
    product_data: str = Form(...),
    image: Optional[UploadFile] = File(None)
):
    product_dict = json.loads(product_data)
    product = Product(**product_dict)
    return await product_service.update_product(product_id, product, image)
