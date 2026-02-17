from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import Optional

@dataclass
class Category:
    """
    Domain entity representing a product category.

    Attributes:
        id (UUID): Unique identifier.
        name (str): Name of the category.
        description (str): Optional description.
        active (bool): Whether the category is active.
        created_at (datetime): Creation timestamp.
        updated_at (datetime): Last update timestamp.
    """
    id: UUID
    name: str
    description: Optional[str]
    active: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(cls, name: str, description: str = None) -> "Category":
        """
        Factory method to create a new Category.
        """
        if not name:
            raise ValueError("Category name cannot be empty.")
            
        now = datetime.now(timezone.utc)
        return cls(
            id=uuid4(),
            name=name,
            description=description,
            active=True,
            created_at=now,
            updated_at=now,
        )

    def update(self, name: str = None, description: str = None, active: bool = None):
        """
        Updates category attributes.
        """
        if name is not None:
            if not name:
                raise ValueError("Category name cannot be empty.")
            self.name = name
        
        if description is not None:
            self.description = description
            
        if active is not None:
            self.active = active
            
        self.updated_at = datetime.now(timezone.utc)
