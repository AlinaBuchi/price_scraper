from fastapi import APIRouter
from .product_api import product_router

api_endpoints = APIRouter()
api_endpoints.include_router(product_router)