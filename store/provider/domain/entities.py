from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import Optional
import re

@dataclass
class Provider:
    """
    Domain entity representing a supplier/provider.
    """
    id: UUID
    name: str
    phone: Optional[str]
    email: Optional[str]
    address: Optional[str]
    active: bool
    created_at: datetime
    updated_at: datetime

    EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    @classmethod
    def create(cls, name: str, phone: str = None, email: str = None, address: str = None) -> "Provider":
        if not name:
            raise ValueError("Provider name cannot be empty.")
        
        if email and not re.match(cls.EMAIL_REGEX, email):
            raise ValueError("Invalid email format.")

        now = datetime.now(timezone.utc)
        return cls(
            id=uuid4(),
            name=name,
            phone=phone,
            email=email,
            address=address,
            active=True,
            created_at=now,
            updated_at=now,
        )

    def update(self, name: str = None, phone: str = None, email: str = None, address: str = None, active: bool = None):
        if name is not None:
            if not name:
                raise ValueError("Provider name cannot be empty.")
            self.name = name
        
        if email is not None:
            if email and not re.match(self.EMAIL_REGEX, email):
                raise ValueError("Invalid email format.")
            self.email = email

        if phone is not None:
            self.phone = phone
            
        if address is not None:
            self.address = address
            
        if active is not None:
            self.active = active
            
        self.updated_at = datetime.now(timezone.utc)
