import pytest
from uuid import uuid4
from decimal import Decimal
from store.sale.domain.entities import Sale
from store.sale.application.use_cases.add_sale_detail import AddSaleDetail
from store.sale.application.dtos import AddSaleDetailDTO
# Changed import to not rely on 'tests' being a package if running from root without proper path
# But actually let's try relative import if run as module? No, pytest runs as script.
# Let's keep absolute but ensure path is correct.
from tests.fakes.fake_sale_repository import FakeSaleRepository

def test_add_sale_detail_success():
    """Test successfully adding a detail to an existing sale."""
    repo = FakeSaleRepository()
    sale = Sale.create()
    repo.save(sale)
    
    use_case = AddSaleDetail(repo)
    
    plant_item_id = uuid4()
    dto = AddSaleDetailDTO(
        sale_id=sale.id,
        plant_item_id=plant_item_id,
        quantity=2,
        unit_price=Decimal("10.0")
    )
    
    response = use_case.execute(dto)
    
    assert response.id == sale.id
    assert len(response.details) == 1
    assert response.total == Decimal("20.0")
    
    # Verify persistence
    saved_sale = repo.get_by_id(sale.id)
    assert len(saved_sale.details) == 1
    assert saved_sale.details[0].plant_item_id == plant_item_id

def test_add_sale_detail_sale_not_found():
    """Test that adding a detail to a non-existent sale raises ValueError."""
    repo = FakeSaleRepository()
    use_case = AddSaleDetail(repo)
    
    dto = AddSaleDetailDTO(
        sale_id=uuid4(),
        plant_item_id=uuid4(),
        quantity=1,
        unit_price=Decimal("10.0")
    )
    
    with pytest.raises(ValueError, match="not found"):
        use_case.execute(dto)
