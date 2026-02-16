from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from uuid import UUID

@dataclass
class CreatePlantItemDTO:
    name: str
    description: str
    price: float
    stock: int

@dataclass
class UpdatePlantItemDTO:
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None

@dataclass
class PlantItemResponseDTO:
    id: UUID
    name: str
    description: str
    price: float
    stock: int
    is_available: bool
    created_at: datetime

@dataclass
class ListPlantItemsQueryDTO:
    page: int = 1
    page_size: int = 10
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    is_available: Optional[bool] = None
    name_contains: Optional[str] = None

@dataclass
class PaginatedPlantItemsDTO:
    items: List[PlantItemResponseDTO]
    page: int
    page_size: int
    total_count: int
    total_pages: int
