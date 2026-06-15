from ..core.database import db
from ..models.product import Product
import logging

logger = logging.getLogger("ssp-product-service")

class ProductRepository:
    def _get_collection(self):
        return db.client.ssp_products.products

    # This method acts as our "table creation" or index initialization
    # In MongoDB, collections are created automatically, but indexes should be enforced
    async def initialize_indexes(self):
        logger.info("Initializing database indexes...")
        try:
            # Ensure product 'id' is unique
            await self._get_collection().create_index("id", unique=True)
            # Create text index for basic searching if not using OpenSearch for everything
            await self._get_collection().create_index([("name", "text"), ("category", "text")])
            logger.info("Database indexes initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize indexes: {e}")

    async def get_all_products(self):
        products = []
        try:
            cursor = self._get_collection().find({})
            async for document in cursor:
                products.append(Product(**document))
            return products
        except Exception as e:
            logger.error(f"Repository Error fetching products: {e}")
            raise

    async def get_product_by_id(self, product_id: str):
        try:
            document = await self._get_collection().find_one({"id": product_id})
            if document:
                return Product(**document)
            return None
        except Exception as e:
            logger.error(f"Repository Error fetching product {product_id}: {e}")
            raise

    async def create_product(self, product: Product):
        try:
            await self._get_collection().insert_one(product.dict())
            return product
        except Exception as e:
            logger.error(f"Repository Error creating product {product.id}: {e}")
            raise

    async def update_product(self, product_id: str, product: Product):
         try:
             await self._get_collection().replace_one({"id": product_id}, product.dict())
             return product
         except Exception as e:
             logger.error(f"Repository Error updating product {product_id}: {e}")
             raise
