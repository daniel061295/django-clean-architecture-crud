from typing import Any, List, Optional, Tuple, TypeVar, Generic
from abc import ABC, abstractmethod
import boto3
from boto3.dynamodb.conditions import Attr
import logging
from django.conf import settings
from core.exceptions import DynamoDBClientError
from core.domain.repositories import BaseRepository

T = TypeVar('T')

class DynamoDBBaseRepository(BaseRepository[T], ABC):
    """
    Base Repository for DynamoDB (Clean Architecture - Infrastructure Layer).
    
    This class implements the BaseRepository interface by encapsulating boto3 interactions.
    Concrete repositories must inherit from this class and implement the mapping
    methods `_to_db_dict` and `_to_domain_entity`.
    """
    
    def __init__(self, table_name: str, pk_name: str, sk_name: Optional[str] = None):
        """
        Initializes the DynamoDB repository with table and key names.
        
        Args:
            table_name: The name of the DynamoDB table.
            pk_name: The name of the Partition Key.
            sk_name: The name of the Sort Key (optional).
        """
        self.table_name = table_name
        self.pk_name = pk_name
        self.sk_name = sk_name
        
        # Initialize boto3 resource using django settings
        self.dynamodb = boto3.resource(
            "dynamodb", 
            region_name=getattr(settings, 'AWS_REGION', 'us-east-1'),
            aws_access_key_id=getattr(settings, 'AWS_ACCESS_KEY_ID', None),
            aws_secret_access_key=getattr(settings, 'AWS_SECRET_ACCESS_KEY', None)
        )
        self.table = self.dynamodb.Table(self.table_name)

    @abstractmethod
    def _to_db_dict(self, entity: T) -> dict:
        """Converts a domain entity -> raw dictionary for DynamoDB."""
        pass

    @abstractmethod
    def _to_domain_entity(self, item_dict: dict) -> T:
        """Converts a raw dictionary from DynamoDB -> domain entity."""
        pass

    def _build_key(self, entity_id: Any) -> dict:
        """
        Builds the key dictionary for DynamoDB queries.
        Can be overridden if entity_id needs parsing (e.g., UUID to string).
        """
        return {self.pk_name: str(entity_id)}

    def _exists_by_attribute(self, attribute_name: str, attribute_value: Any) -> bool:
        """
        Checks if an item with the given attribute value exists.
        """
        try:
            response = self.table.scan(
                FilterExpression=Attr(attribute_name).eq(attribute_value)
            )
            return len(response.get("Items", [])) > 0
        except Exception as e:
            logging.error(f"Error in _exists_by_attribute for table {self.table_name}: {e}")
            raise DynamoDBClientError(f"Failed to check if attribute exists: {e}")

    def save(self, entity: T) -> T:
        """
        Inserts or replaces an item in DynamoDB and returns it.
        """
        try:
            item_dict = self._to_db_dict(entity)
            self.table.put_item(Item=item_dict)
            return self._to_domain_entity(item_dict)
        except Exception as e:
            logging.error(f"Error in save for table {self.table_name}: {e}")
            raise DynamoDBClientError(f"Failed to save item: {e}")

    def get_by_id(self, entity_id: Any) -> Optional[T]:
        """
        Retrieves an entity by its unique identifier.
        """
        try:
            key_dict = self._build_key(entity_id)
            response = self.table.get_item(Key=key_dict)
            if "Item" in response:
                return self._to_domain_entity(response["Item"])
            return None
        except Exception as e:
            logging.error(f"Error in get_by_id for table {self.table_name}: {e}")
            raise DynamoDBClientError(f"Failed to get item by id: {e}")

    def delete(self, entity_id: Any) -> None:
        """
        Deletes an entity by its unique identifier.
        """
        try:
            key_dict = self._build_key(entity_id)
            self.table.delete_item(Key=key_dict)
        except Exception as e:
            logging.error(f"Error in delete for table {self.table_name}: {e}")
            raise DynamoDBClientError(f"Failed to delete item: {e}")

    def list(self, page: int, page_size: int, filters: dict) -> Tuple[List[T], int]:
        """
        Lists entities with pagination.
        Note: DynamoDB scan does not support native offset-based pagination.
        This implementation does a basic scan and slices in memory. For large 
        datasets, cursor-based pagination (ExclusiveStartKey) should be preferred.
        """
        items: List[dict] = []
        try:
            # We perform a scan. For a real production app with large tables, 
            # consider refactoring to return the LastEvaluatedKey.
            response = self.table.scan()
            items.extend(response.get("Items", []))

            while "LastEvaluatedKey" in response:
                response = self.table.scan(
                    ExclusiveStartKey=response["LastEvaluatedKey"]
                )
                items.extend(response.get("Items", []))
            
            # Convert
            domain_items = [self._to_domain_entity(i) for i in items]
            
            # Basic in-memory pagination
            start_index = (page - 1) * page_size
            end_index = start_index + page_size
            
            paginated_items = domain_items[start_index:end_index]
            
            return paginated_items, len(domain_items)

        except Exception as e:
            logging.error(f"Error in list scan for table {self.table_name}: {e}")
            raise DynamoDBClientError(f"Failed to list items: {e}")

    def _query_items(self, key_condition: Any) -> List[T]:
        """
        Queries items using a KeyConditionExpression and returns entities.
        """
        try:
            response = self.table.query(KeyConditionExpression=key_condition)
            return [self._to_domain_entity(i) for i in response.get("Items", [])]
        except Exception as e:
            logging.error(f"Error in query for table {self.table_name}: {e}")
            raise DynamoDBClientError(f"Failed to query items: {e}")

