import unittest
from unittest.mock import Mock, MagicMock
from uuid import uuid4
from store.application.dtos import CreatePlantItemDTO
from store.application.use_cases.create_plant_item import CreatePlantItem
from store.domain.entities import PlantItem


class TestCreatePlantItemUseCase(unittest.TestCase):
    def setUp(self):
        self.repository = Mock()
        self.use_case = CreatePlantItem(self.repository)

    def test_execute_creates_and_saves_item(self):
        dto = CreatePlantItemDTO(name="Tulip", description="Yellow tulip", price=5.0, stock=50)

        # Explain to mock what to return when save is called
        def save_side_effect(item):
            return item

        self.repository.save.side_effect = save_side_effect

        result = self.use_case.execute(dto)

        self.repository.save.assert_called_once()
        self.assertEqual(result.name, dto.name)
        self.assertEqual(result.price, dto.price)
        self.assertTrue(result.is_available)
