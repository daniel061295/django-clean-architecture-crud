from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from uuid import UUID


@dataclass
class CreatePlantItemDTO:
    """
    Data Transfer Object for creating a new PlantItem.

    Attributes:
        name (str): Name of the plant.
        description (str): Description.
        price (float): Price.
        stock (int): Initial stock.
    """

    name: str
    description: str
    price: float
    stock: int


@dataclass
class UpdatePlantItemDTO:
    """
    Data Transfer Object for updating an existing PlantItem.
    All fields are optional.

    Attributes:
        name (Optional[str]): New name.
        description (Optional[str]): New description.
        price (Optional[float]): New price.
        stock (Optional[int]): New stock.
    """

    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None


@dataclass
class PlantItemResponseDTO:
    """
    Data Transfer Object for PlantItem responses.

    Attributes:
        id (UUID): Unique identifier.
        name (str): Name.
        description (str): Description.
        price (float): Price.
        stock (int): Stock.
        is_available (bool): Availability status.
        created_at (datetime): Creation date.
    """

    id: UUID
    name: str
    description: str
    price: float
    stock: int
    is_available: bool
    created_at: datetime


@dataclass
class ListPlantItemsQueryDTO:
    """
    Data Transfer Object for listing query parameters.

    Attributes:
        page (int): Page number.
        page_size (int): Items per page.
        min_price (Optional[float]): Filter by minimum price.
        max_price (Optional[float]): Filter by maximum price.
        is_available (Optional[bool]): Filter by availability.
        name_contains (Optional[str]): Filter by name substring.
    """

    page: int = 1
    page_size: int = 10
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    is_available: Optional[bool] = None
    name_contains: Optional[str] = None


@dataclass
class PaginatedPlantItemsDTO:
    """
    Data Transfer Object for paginated list responses.

    Attributes:
        items (List[PlantItemResponseDTO]): List of items in current page.
        page (int): Current page number.
        page_size (int): Items per page.
        total_count (int): Total number of items across all pages.
        total_pages (int): Total number of pages.
    """

    items: List[PlantItemResponseDTO]
    page: int
    page_size: int
    total_count: int
    total_pages: int
