from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID
from typing import List, Optional
from decimal import Decimal

@dataclass
class SaleDetailDTO:
    plant_item_id: UUID
    quantity: int
    unit_price: Decimal

@dataclass
class CreateSaleDTO:
    # Empty for now as creation is just "Starting" a sale, 
    # OR we can allow creating with initial items.
    initial_items: List[SaleDetailDTO] = field(default_factory=list)

@dataclass
class AddSaleDetailDTO:
    sale_id: UUID
    plant_item_id: UUID
    quantity: int
    unit_price: Decimal

@dataclass
class SaleDetailResponseDTO:
    id: UUID
    plant_item_id: UUID
    quantity: int
    unit_price: Decimal
    subtotal: Decimal

@dataclass
class SaleResponseDTO:
    id: UUID
    date: datetime
    total: Decimal
    status: str
    created_at: datetime
    details: List[SaleDetailResponseDTO]
