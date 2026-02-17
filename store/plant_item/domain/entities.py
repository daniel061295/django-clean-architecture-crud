from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import Optional
from store.plant_item.domain.exceptions import InvalidStockError, InvalidPriceError


@dataclass
class PlantItem:
    """
    Domain entity representing a plant item in the store.

    Attributes:
        id (UUID): Unique identifier.
        name (str): Name of the plant.
        description (str): Description of the plant.
        price (float): Price of the plant.
        stock (int): Available stock.
        created_at (datetime): Creation timestamp.
        is_available (bool): Availability status based on stock.
    """

    id: UUID
    name: str
    description: str
    price: float
    stock: int
    created_at: datetime
    is_available: bool = field(init=False)

    def __post_init__(self):
        """
        Post-initialization hook to validate and update internal state.
        """
        self.validate()
        self.update_availability()

    def validate(self):
        """
        Validates the entity invariants.

        Raises:
            InvalidPriceError: If price is negative.
            InvalidStockError: If stock is negative.
        """
        if self.price < 0:
            raise InvalidPriceError("Price cannot be negative.")
        if self.stock < 0:
            raise InvalidStockError("Stock cannot be negative.")

    def update_availability(self):
        """Updates the is_available flag based on current stock."""
        self.is_available = self.stock > 0

    @classmethod
    def create(cls, name: str, description: str, price: float, stock: int) -> "PlantItem":
        """
        Factory method to create a new PlantItem with a generated UUID and timestamp.

        Args:
            name (str): Name of the plant.
            description (str): Description.
            price (float): Price.
            stock (int): Stock quantity.

        Returns:
            PlantItem: The created entity.
        """
        return cls(
            id=uuid4(),
            name=name,
            description=description,
            price=price,
            stock=stock,
            created_at=datetime.now(timezone.utc),
        )

    def update(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        price: Optional[float] = None,
        stock: Optional[int] = None,
    ):
        """
        Updates the entity attributes and re-validates.

        Args:
            name (Optional[str]): New name.
            description (Optional[str]): New description.
            price (Optional[float]): New price.
            stock (Optional[int]): New stock.
        """
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        if price is not None:
            self.price = price
        if stock is not None:
            self.stock = stock

        self.validate()
        self.update_availability()
