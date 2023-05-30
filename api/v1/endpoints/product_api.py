from fastapi import APIRouter, HTTPException, Query
from database import MongoConnector
from bson.objectid import ObjectId
from product import Product
import math

product_router = APIRouter(prefix="/products", tags=["products"])
connector = MongoConnector()


@product_router.get("", tags=['products'])
def get_items(page: int = Query(1, ge=1), per_page: int = Query(10, ge=1, le=100)):
    skip = (page - 1) * per_page
    limit = per_page

    products = connector.list_paginated("products", skip=skip, limit=limit, projection={'price_history': 0})
    products_data = []
    for product in products:
        product['_id'] = str(product['_id'])

        products_data.append(product)

    total_items = connector.count("products")
    total_pages = math.ceil(total_items / limit)
    current_page = math.ceil((skip + 1) / limit)
    metadata = {
        "total_items": total_items,
        "items_per_page": limit,
        "total_pages": total_pages,
        "current_page": current_page
    }

    return {"metadata": metadata, "items": products_data}


@product_router.get("/{sku}", tags=['products'])
def get_item(sku: int):
    product = connector.read_sku("products", sku, projection={'price_history': 0})
    if product is None:
        return HTTPException(status_code=404, detail="Product not found")

    product['_id'] = str(product['_id'])

    return product


@product_router.put("/{obj_id}", tags=['products'])
def update_item(obj_id: str, item: Product):
    product = connector.read("products", obj_id)
    if product is None:
        return HTTPException(status_code=404, detail="Product not found")

    result = connector.update_one("products", {"_id": ObjectId(obj_id)}, item.dict())

    return result


@product_router.post("", tags=['products'])
def save_item(item: Product):
    product = connector.insert_one("products", item.dict())

    return str(product)


@product_router.delete("/{obj_id}", tags=['products'])
def delete_item(obj_id: str):
    product = connector.read("products", obj_id)
    if product is None:
        return HTTPException(status_code=404, detail="Product not found")

    result = connector.delete_one("products", {"_id": ObjectId(obj_id)})

    return result


@product_router.get("/{sku}/history", tags=['products'])
def get_item_history(sku: int):
    product = connector.read_sku("products", sku)
    if product is None:
        return HTTPException(status_code=404, detail="Product not found")

    history = product.get("price_history")
    if history is None:
        return HTTPException(status_code=404, detail="Product history not found")

    return history
