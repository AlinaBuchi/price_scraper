from abc import ABC, abstractmethod


class Singleton(object):
    instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.instance:
            cls.instance = super().__new__(cls)
        return cls.instance


class StorageObject(ABC):

    @abstractmethod
    def select_collection(self, collection_name):
        raise NotImplementedError("Function is not implemented")

    @abstractmethod
    def insert_one(self, collection, document):
        raise NotImplementedError("Function is not implemented")

    @abstractmethod
    def insert_many(self, collection, documents):
        raise NotImplementedError("Function is not implemented")

    @abstractmethod
    def read(self, collection, search_params):
        raise NotImplementedError("Function is not implemented")

    @abstractmethod
    def update_one(self, collection, search_params, to_update):
        raise NotImplementedError("Function is not implemented")

    @abstractmethod
    def delete_one(self, collection, search_params):
        raise NotImplementedError("Function is not implemented")
