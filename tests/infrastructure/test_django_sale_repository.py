import pytest
from decimal import Decimal
from uuid import uuid4
from store.sale.domain.entities import Sale, SaleDetail
from store.sale.infrastructure.repositories import DjangoSaleRepository

@pytest.mark.django_db
def test_save_and_get_sale():
    """Test saving a sale to the database and retrieving it."""
    repo = DjangoSaleRepository()
    sale = Sale.create()
    
    saved_sale = repo.save(sale)
    assert saved_sale.id == sale.id
    
    retrieved_sale = repo.get_by_id(sale.id)
    assert retrieved_sale is not None
    assert retrieved_sale.id == sale.id
    assert retrieved_sale.total == sale.total

@pytest.mark.django_db
def test_save_sale_with_details():
    """Test saving a sale with details."""
    repo = DjangoSaleRepository()
    sale = Sale.create()
    
    plant_item_id = uuid4()
    # We might need to create a PlantItem in DB because of foreign key constraints?
    # DjangoSaleRepository uses SaleMapper which uses Models.
    # SaleDetailModel likely has a ForeignKey to PlantItemModel?
    # Let's check models. usually it does. But SaleDetail has plant_item_id.
    # If SaleDetailModel structure requires a real PlantItem, we must create it.
    # Assuming for now we need it. But let's check `store/sale/infrastructure/models.py`.
    
    # If FK is strictly enforced, this test will fail.
    # However, let's try assuming standard behavior where UUID field or FK exists.
    # Given clean architecture often decouples ID references, it might be just a UUIDField.
    # But usually in Django it's a ForeignKey.
    # Let's try simple first.
    
    sale.add_detail(plant_item_id, 2, Decimal("10.0"))
    
    try:
        repo.save(sale)
    except Exception as e:
        # If it fails due to FK constraint, we know we need to create PlantItem.
        pytest.fail(f"Failed to save sale with details: {e}")
        
    retrieved = repo.get_by_id(sale.id)
    assert len(retrieved.details) == 1
    assert retrieved.total == Decimal("20.0")

@pytest.mark.django_db
def test_list_sales():
    """Test listing sales with pagination."""
    repo = DjangoSaleRepository()
    
    for _ in range(5):
        repo.save(Sale.create())
        
    sales, count = repo.list(page=1, page_size=2, filters={})
    
    assert len(sales) == 2
    assert count == 5
