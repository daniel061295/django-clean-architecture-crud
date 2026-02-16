from django.test import TestCase
from store.domain.entities import PlantItem
from store.infrastructure.repositories import DjangoPlantItemRepository
from store.infrastructure.models import PlantItemModel
from store.infrastructure.mappers import PlantItemMapper
from decimal import Decimal

class DjangoPlantItemRepositoryTestCase(TestCase):
    def setUp(self):
        self.repository = DjangoPlantItemRepository()
        self.item_data = {
            "name": "Test Plant",
            "description": "Test Description",
            "price": Decimal("10.50"),
            "stock": 5
        }

    def test_save_and_get(self):
        item = PlantItem.create(**self.item_data)
        self.repository.save(item)
        
        saved_item = self.repository.get_by_id(item.id)
        self.assertIsNotNone(saved_item)
        self.assertEqual(saved_item.name, item.name)
        self.assertEqual(saved_item.price, item.price)
        
        # Verify it exists in DB
        self.assertTrue(PlantItemModel.objects.filter(id=item.id).exists())

    def test_list_pagination(self):
        # Create 15 items
        for i in range(15):
            item = PlantItem.create(
                name=f"Plant {i}",
                description="Desc",
                price=Decimal("10.00"),
                stock=5
            )
            self.repository.save(item)
            
        # Test page 1 (default size might be 10 or generic)
        items, count = self.repository.list(page=1, page_size=10, filters={})
        self.assertEqual(len(items), 10)
        self.assertEqual(count, 15)
        
        # Test page 2
        items, count = self.repository.list(page=2, page_size=10, filters={})
        self.assertEqual(len(items), 5)
        
        # Test filtering
        filtered_items, count = self.repository.list(page=1, page_size=10, filters={"name_contains": "Plant 1"})
        # Should match Plant 1, Plant 10, Plant 11, etc.
        self.assertTrue(count >= 1)
        self.assertTrue(all("Plant 1" in item.name for item in filtered_items))

    def test_delete(self):
        item = PlantItem.create(**self.item_data)
        self.repository.save(item)
        
        self.assertTrue(self.repository.exists(item.id))
        self.repository.delete(item.id)
        self.assertFalse(self.repository.exists(item.id))
        
    def test_update(self):
        item = PlantItem.create(**self.item_data)
        self.repository.save(item)
        
        item.update(name="Updated Name")
        self.repository.save(item)
        
        updated_item = self.repository.get_by_id(item.id)
        self.assertEqual(updated_item.name, "Updated Name")

class PlantItemMapperTestCase(TestCase):
    def test_to_domain(self):
        model = PlantItemModel.objects.create(
            name="Model Plant",
            description="Model Desc",
            price=Decimal("20.00"),
            stock=10,
            is_available=True
        )
        
        entity = PlantItemMapper.to_domain(model)
        self.assertIsInstance(entity, PlantItem)
        self.assertEqual(entity.id, model.id)
        self.assertEqual(entity.name, model.name)
        
    def test_to_db(self):
        entity = PlantItem.create(
            name="Entity Plant",
            description="Entity Desc",
            price=Decimal("30.00"),
            stock=5
        )
        
        model = PlantItemMapper.to_db(entity)
        self.assertIsInstance(model, PlantItemModel)
        self.assertEqual(model.id, entity.id)
        self.assertEqual(model.name, entity.name)
