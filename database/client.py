from pymongo import MongoClient
from pymongo.collection import Collection
from typing import List, Any
from bson.objectid import ObjectId


from .base import Singleton, StorageObject


class MongoConnector(Singleton, StorageObject):

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # for docker usage:
            # cls._instance.client = MongoClient("mongodb://database:27017")
            # for other cases:
            cls._instance.client = MongoClient("mongodb://localhost:27017")
            cls._instance.collections = {
                'products': cls._instance.client["web_scraper"]["products"],
                'urls': cls._instance.client["web_scraper"]["urls"]
            }
        return cls._instance

    def select_collection(self, collection_name: str) -> Collection:
        if collection_name not in self.collections:
            raise ValueError("Invalid collection name")
        return self.collections[collection_name]

    def insert_one(self, collection_name: str, document: dict) -> Any:
        collection = self.select_collection(collection_name)
        result = collection.insert_one(document)

        return result.inserted_id

    def insert_many(self, collection_name: str, documents: List[dict]) -> None:
        collection = self.select_collection(collection_name)
        collection.insert_many(documents)

    def read(self, collection_name: str, item_id: str) -> dict:
        collection = self.select_collection(collection_name)
        result = collection.find_one({"_id": ObjectId(item_id)})

        return result

    def read_sku(self, collection_name: str, sku: int | str, projection=None) -> dict:
        collection = self.select_collection(collection_name)
        if not projection:
            result = collection.find_one({"sku": sku})
        else:
            result = collection.find_one({"sku": sku}, projection)

        return result

    def list(self, collection_name: str, search_params: dict = None) -> List[dict]:
        collection = self.select_collection(collection_name)
        result = collection.find(search_params)
        items = list(result)

        return items

    def list_paginated(self, collection_name: str, skip: int = 0, limit: int = 10, projection=None) -> List[dict]:
        collection = self.select_collection(collection_name)
        if not projection:
            result = collection.find({}).skip(skip).limit(limit)
        else:
            result = collection.find({}, projection).skip(skip).limit(limit)
        items = list(result)

        return items

    def count(self, collection_name: str):
        collection = self.select_collection(collection_name)

        return collection.count_documents({})

    def update_one(self, collection_name: str, search_params: dict, to_update: dict) -> dict[str, Any]:
        collection = self.select_collection(collection_name)
        result = collection.update_one(search_params, {'$set': to_update})

        return result.raw_result

    def delete_one(self, collection_name: str, search_params: dict) -> dict[str, Any]:
        collection = self.select_collection(collection_name)
        result = collection.delete_one(search_params)

        return result.raw_result

    def get_id(self, collection_name: str, params: dict) -> None | str:
        collection = self.select_collection(collection_name)
        obj = collection.find_one(params)
        if obj:
            return str(obj["_id"])
        else:
            return None

    def update_history(self, collection_name: str, sku: int | str, update_dict: dict) -> None:
        collection = self.select_collection(collection_name)
        collection.update_one({'sku': sku}, {'$push': {'price_history': {'$each': [update_dict]}}})


