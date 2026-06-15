from ..repositories.product_repository import ProductRepository
from ..models.product import Product
from fastapi import HTTPException, UploadFile
import logging
import boto3
import os
import uuid

logger = logging.getLogger("ssp-product-service")

# S3 Configuration
S3_BUCKET_NAME = os.environ.get("PRODUCT_IMAGES_BUCKET_NAME", "ssp-product-images")
s3_client = boto3.client('s3', region_name=os.environ.get("AWS_REGION", "us-east-1"))

class ProductService:
    def __init__(self):
        self.repository = ProductRepository()

    async def get_all_products(self):
        return await self.repository.get_all_products()

    async def get_product_by_id(self, product_id: str):
        product = await self.repository.get_product_by_id(product_id)
        if not product:
            logger.warning(f"Service: Product not found: {product_id}")
            raise HTTPException(status_code=404, detail="Product not found")
        return product

    async def _upload_image_to_s3(self, image: UploadFile, product_id: str) -> str:
        """Uploads an image to S3 and returns the public URL."""
        if not image:
            return None
            
        file_extension = image.filename.split('.')[-1]
        unique_filename = f"{product_id}_{uuid.uuid4().hex}.{file_extension}"
        
        try:
            logger.info(f"Uploading image {unique_filename} to S3 bucket {S3_BUCKET_NAME}")
            s3_client.upload_fileobj(
                image.file,
                S3_BUCKET_NAME,
                unique_filename,
                ExtraArgs={'ContentType': image.content_type} # Ensure correct MIME type
            )
            # Assuming the bucket is public or you have a CloudFront distribution in front of it
            # In production, use CloudFront domain instead of direct S3 URL
            image_url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{unique_filename}"
            return image_url
        except Exception as e:
            logger.error(f"Failed to upload image to S3: {e}")
            raise HTTPException(status_code=500, detail="Image upload failed")

    async def create_product(self, product: Product, image: UploadFile = None):
        existing_product = await self.repository.get_product_by_id(product.id)
        if existing_product:
            logger.warning(f"Service: Attempt to create duplicate product: {product.id}")
            raise HTTPException(status_code=400, detail="Product ID already exists")
        
        # Calculate selling price if discount is provided
        if product.discount_percent and product.discount_percent > 0:
            product.selling_price = product.mrp - (product.mrp * (product.discount_percent / 100))
        else:
            product.selling_price = product.mrp

        if image:
            product.image_url = await self._upload_image_to_s3(image, product.id)
            
        logger.info(f"Service: Creating product: {product.id}")
        return await self.repository.create_product(product)

    async def update_product(self, product_id: str, product_update: Product, image: UploadFile = None):
        existing = await self.repository.get_product_by_id(product_id)
        if not existing:
             raise HTTPException(status_code=404, detail="Product not found")
             
        # Logic to update image, recalculate prices, and call repository.update()
        # (Placeholder for brevity)
        if image:
            product_update.image_url = await self._upload_image_to_s3(image, product_id)
        
        logger.info(f"Service: Updating product: {product_id}")
        return await self.repository.update_product(product_id, product_update)
