import pytest
from uuid import uuid4
from decimal import Decimal
from store.sale.domain.entities import Sale, SaleDetail, SaleStatus

def test_create_sale():
    """Test that a sale is created with correct initial values."""
    sale = Sale.create()
    
    assert sale.id is not None
    assert sale.date is not None
    assert sale.total == Decimal("0.0")
    assert sale.status == SaleStatus.PENDIENTE
    assert sale.created_at is not None
    assert sale.details == []

def test_add_detail_to_sale():
    """Test adding a detail to a pending sale."""
    sale = Sale.create()
    plant_item_id = uuid4()
    quantity = 2
    unit_price = Decimal("10.50")
    
    sale.add_detail(plant_item_id, quantity, unit_price)
    
    assert len(sale.details) == 1
    detail = sale.details[0]
    assert detail.plant_item_id == plant_item_id
    assert detail.quantity == quantity
    assert detail.unit_price == unit_price
    assert detail.subtotal == Decimal("21.00")
    assert sale.total == Decimal("21.00")

def test_add_detail_to_non_pending_sale_fails():
    """Test that adding specific detail to a non-pending sale raises ValueError."""
    sale = Sale.create()
    sale.status = SaleStatus.COMPLETADA
    
    with pytest.raises(ValueError, match="Cannot add details to a non-pending sale"):
        sale.add_detail(uuid4(), 1, Decimal("10.0"))

def test_create_sale_detail_validations():
    """Test validation logic when creating a SaleDetail."""
    sale_id = uuid4()
    plant_item_id = uuid4()
    
    # Test valid creation
    detail = SaleDetail.create(sale_id, plant_item_id, 1, Decimal("10.0"))
    assert detail.quantity == 1
    
    # Test invalid quantity
    with pytest.raises(ValueError, match="Quantity must be greater than 0"):
        SaleDetail.create(sale_id, plant_item_id, 0, Decimal("10.0"))
        
    # Test invalid price
    with pytest.raises(ValueError, match="Unit price must be greater than 0"):
        SaleDetail.create(sale_id, plant_item_id, 1, Decimal("0.0"))

def test_calculate_total():
    """Test total calculation with multiple details."""
    sale = Sale.create()
    sale.add_detail(uuid4(), 2, Decimal("10.0")) # 20.0
    sale.add_detail(uuid4(), 3, Decimal("5.0"))  # 15.0
    
    assert sale.total == Decimal("35.0")

def test_complete_sale_success():
    """Test successfully completing a sale."""
    sale = Sale.create()
    sale.add_detail(uuid4(), 1, Decimal("10.0"))
    
    sale.complete()
    
    assert sale.status == SaleStatus.COMPLETADA

def test_complete_sale_failures():
    """Test failure scenarios for completing a sale."""
    # Test completing empty sale
    sale = Sale.create()
    with pytest.raises(ValueError, match="Cannot complete a sale with no details"):
        sale.complete()
        
    # Test completing already completed sale
    sale.add_detail(uuid4(), 1, Decimal("10.0"))
    sale.complete()
    with pytest.raises(ValueError, match="Only pending sales can be completed"):
        sale.complete()

def test_cancel_sale():
    """Test canceling a sale."""
    sale = Sale.create()
    sale.cancel()
    assert sale.status == SaleStatus.CANCELADA
    
    # Test canceling completed sale
    sale = Sale.create()
    sale.add_detail(uuid4(), 1, Decimal("10.0"))
    sale.complete()
    
    with pytest.raises(ValueError, match="Cannot cancel a completed sale"):
        sale.cancel()
