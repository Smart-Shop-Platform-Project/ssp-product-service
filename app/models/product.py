from pydantic import BaseModel
from typing import Optional

class Product(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    mrp: float               # Maximum Retail Price
    discount_percent: Optional[float] = 0.0
    selling_price: float
    category: str
    image_url: Optional[str] = None # Will store the S3 object URL
