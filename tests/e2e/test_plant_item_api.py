import pytest
from rest_framework.test import APIClient
from rest_framework import status
from store.plant_item.infrastructure.models import PlantItemModel
from uuid import uuid4

@pytest.mark.django_db
class TestPlantItemAPI:
    def setup_method(self):
        self.client = APIClient()
        self.base_url = "/api/plant-items/"

    def test_create_plant_item(self):
        payload = {
            "name": "Orchid",
            "description": "Beautiful",
            "price": 25.50,
            "stock": 10
        }
        response = self.client.post(self.base_url, payload, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert "id" in response.data
        assert response.data["name"] == "Orchid"
        
        # Verify DB
        assert PlantItemModel.objects.count() == 1

    def test_list_plant_items(self):
        PlantItemModel.objects.create(name="P1", description="D1", price=10.0, stock=5)
        PlantItemModel.objects.create(name="P2", description="D2", price=20.0, stock=5)
        
        response = self.client.get(self.base_url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["data"]) >= 2

    def test_retrieve_plant_item(self):
        item = PlantItemModel.objects.create(name="P1", description="D1", price=10.0, stock=5)
        
        url = f"{self.base_url}{item.id}/"
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == str(item.id)

    def test_update_plant_item(self):
        item = PlantItemModel.objects.create(name="P1", description="D1", price=10.0, stock=5)
        
        payload = {
            "name": "Updated P1",
            "description": "Updated D1",
            "price": 15.0,
            "stock": 20
        }
        url = f"{self.base_url}{item.id}/"
        response = self.client.put(url, payload, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Updated P1"
        assert float(response.data["price"]) == 15.0
        
        item.refresh_from_db()
        assert item.name == "Updated P1"

    def test_delete_plant_item(self):
        item = PlantItemModel.objects.create(name="P1", description="D1", price=10.0, stock=5)
        
        url = f"{self.base_url}{item.id}/"
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        assert PlantItemModel.objects.count() == 0
