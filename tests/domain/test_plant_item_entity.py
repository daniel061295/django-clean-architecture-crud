import pytest
from uuid import UUID
from datetime import datetime
from store.plant_item.domain.entities import PlantItem
from store.plant_item.domain.exceptions import InvalidPriceError, InvalidStockError

def test_create_plant_item_success():
    """Test successful creation of a plant item."""
    name = "Rose"
    description = "Red Rose"
    price = 15.0
    stock = 10
    
    plant = PlantItem.create(name, description, price, stock)
    
    assert isinstance(plant.id, UUID)
    assert plant.name == name
    assert plant.description == description
    assert plant.price == price
    assert plant.stock == stock
    assert plant.is_available is True
    assert isinstance(plant.created_at, datetime)

def test_create_plant_item_negative_price_fails():
    """Test that creating a plant item with negative price fails."""
    with pytest.raises(InvalidPriceError):
        PlantItem.create("Rose", "Desc", -1.0, 10)

def test_create_plant_item_negative_stock_fails():
    """Test that creating a plant item with negative stock fails."""
    with pytest.raises(InvalidStockError):
        PlantItem.create("Rose", "Desc", 10.0, -5)

def test_update_plant_item_success():
    """Test successful update of a plant item."""
    plant = PlantItem.create("Rose", "Desc", 10.0, 5)
    
    plant.update(name="Tulip", price=12.0)
    
    assert plant.name == "Tulip"
    assert plant.price == 12.0
    assert plant.description == "Desc"
    assert plant.stock == 5

def test_update_availability_logic():
    """Test that is_available updates correctly based on stock."""
    plant = PlantItem.create("Rose", "Desc", 10.0, 5)
    assert plant.is_available is True
    
    plant.update(stock=0)
    assert plant.is_available is False
    
    plant.update(stock=3)
    assert plant.is_available is True

def test_update_validation_price():
    """Test validation of price update."""
    plant = PlantItem.create("Rose", "Desc", 10.0, 5)
    
    with pytest.raises(InvalidPriceError):
        plant.update(price=-5.0)

def test_update_validation_stock():
    """Test validation of stock update."""
    plant = PlantItem.create("Rose", "Desc", 10.0, 5)

    with pytest.raises(InvalidStockError):
        plant.update(stock=-1)
