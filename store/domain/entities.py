from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import Optional
from store.domain.exceptions import InvalidStockError, InvalidPriceError

@dataclass
class PlantItem:
    id: UUID
    name: str
    description: str
    price: float
    stock: int
    created_at: datetime
    is_available: bool = field(init=False)

    def __post_init__(self):
        self.validate()
        self.update_availability()

    def validate(self):
        if self.price < 0:
            raise InvalidPriceError("Price cannot be negative.")
        if self.stock < 0:
            raise InvalidStockError("Stock cannot be negative.")

    def update_availability(self):
        self.is_available = self.stock > 0

    @classmethod
    def create(cls, name: str, description: str, price: float, stock: int) -> 'PlantItem':
        return cls(
            id=uuid4(),
            name=name,
            description=description,
            price=price,
            stock=stock,
            created_at=datetime.now(timezone.utc) 
        )

    def update(self, name: Optional[str] = None, description: Optional[str] = None, 
               price: Optional[float] = None, stock: Optional[int] = None):
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
