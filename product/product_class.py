from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Union


class Product(BaseModel):
    product_name: str
    price_history: list[Dict[str, Union[float, datetime]]]
    image: str
    sku: int | str
    recommendations: list[str]
