import unittest
from uuid import uuid4
from datetime import datetime
from store.domain.entities import PlantItem
from store.domain.exceptions import InvalidStockError, InvalidPriceError

class TestPlantItem(unittest.TestCase):
    def test_create_valid_plant_item(self):
        item = PlantItem.create(
            name="Rose",
            description="Beautiful red rose",
            price=10.50,
            stock=100
        )
        self.assertEqual(item.name, "Rose")
        self.assertEqual(item.price, 10.50)
        self.assertTrue(item.is_available)
        self.assertIsInstance(item.id, uuid4().__class__)
        self.assertIsInstance(item.created_at, datetime)

    def test_create_invalid_price(self):
        with self.assertRaises(InvalidPriceError):
            PlantItem.create(name="Rose", description="Desc", price=-10, stock=10)

    def test_create_invalid_stock(self):
        with self.assertRaises(InvalidStockError):
            PlantItem.create(name="Rose", description="Desc", price=10, stock=-5)

    def test_update_availability_on_stock_change(self):
        item = PlantItem.create(name="Rose", description="Desc", price=10, stock=1)
        self.assertTrue(item.is_available)
        
        item.update(stock=0)
        self.assertFalse(item.is_available)
        
        item.update(stock=5)
        self.assertTrue(item.is_available)
