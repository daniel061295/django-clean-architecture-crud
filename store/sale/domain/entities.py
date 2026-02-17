from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4
from enum import Enum
from typing import List, Optional
from decimal import Decimal

class SaleStatus(Enum):
    PENDIENTE = "PENDIENTE"
    COMPLETADA = "COMPLETADA"
    CANCELADA = "CANCELADA"

@dataclass
class SaleDetail:
    id: UUID
    sale_id: UUID
    plant_item_id: UUID
    quantity: int
    unit_price: Decimal
    subtotal: Decimal

    @classmethod
    def create(cls, sale_id: UUID, plant_item_id: UUID, quantity: int, unit_price: Decimal) -> "SaleDetail":
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0.")
        if unit_price <= 0:
            raise ValueError("Unit price must be greater than 0.")
        
        return cls(
            id=uuid4(),
            sale_id=sale_id,
            plant_item_id=plant_item_id,
            quantity=quantity,
            unit_price=unit_price,
            subtotal=Decimal(quantity) * unit_price
        )

@dataclass
class Sale:
    id: UUID
    date: datetime
    total: Decimal
    status: SaleStatus
    created_at: datetime
    details: List[SaleDetail] = field(default_factory=list)

    @classmethod
    def create(cls) -> "Sale":
        now = datetime.now(timezone.utc)
        return cls(
            id=uuid4(),
            date=now,
            total=Decimal("0.0"),
            status=SaleStatus.PENDIENTE,
            created_at=now,
            details=[]
        )

    def add_detail(self, plant_item_id: UUID, quantity: int, unit_price: Decimal):
        if self.status != SaleStatus.PENDIENTE:
             raise ValueError("Cannot add details to a non-pending sale.")
             
        detail = SaleDetail.create(
            sale_id=self.id,
            plant_item_id=plant_item_id,
            quantity=quantity,
            unit_price=unit_price
        )
        self.details.append(detail)
        self.calculate_total()
    
    def calculate_total(self):
        self.total = sum(d.subtotal for d in self.details)

    def complete(self):
        if self.status != SaleStatus.PENDIENTE:
             raise ValueError("Only pending sales can be completed.")
        if not self.details:
             raise ValueError("Cannot complete a sale with no details.")
             
        self.status = SaleStatus.COMPLETADA

    def cancel(self):
         if self.status == SaleStatus.COMPLETADA:
             raise ValueError("Cannot cancel a completed sale.")
         self.status = SaleStatus.CANCELADA
