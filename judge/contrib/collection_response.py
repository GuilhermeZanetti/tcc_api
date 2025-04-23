from typing import Any

from pydantic import BaseModel


class CollectionResponse(BaseModel):
    results: list[Any]

    @classmethod
    def create(
        cls,
        results: list[Any],
    ) -> 'CollectionResponse':
        collection_response = {
            'results': results,
        }

        return cls.model_validate(collection_response)
