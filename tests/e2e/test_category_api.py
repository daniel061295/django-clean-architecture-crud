import pytest
from rest_framework.test import APIClient
from rest_framework import status
from store.category.infrastructure.models import CategoryModel
from uuid import uuid4

@pytest.mark.django_db
class TestCategoryAPI:
    def setup_method(self):
        self.client = APIClient()
        self.base_url = "/api/categories/"

    def test_create_category(self):
        payload = {
            "name": "Electronics",
            "description": "Gadgets",
            "active": True
        }
        response = self.client.post(self.base_url, payload, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert "id" in response.data
        assert response.data["name"] == "Electronics"
        
        # Verify DB
        assert CategoryModel.objects.count() == 1

    def test_list_categories(self):
        CategoryModel.objects.create(name="C1", description="D1", active=True)
        CategoryModel.objects.create(name="C2", description="D2", active=True)
        
        response = self.client.get(self.base_url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["data"]) >= 2

    def test_retrieve_category(self):
        cat = CategoryModel.objects.create(name="C1", description="D1", active=True)
        
        url = f"{self.base_url}{cat.id}/"
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == str(cat.id)

    def test_update_category(self):
        cat = CategoryModel.objects.create(name="C1", description="D1", active=True)
        
        payload = {
            "name": "Updated C1",
            "description": "Updated D1",
            "active": False
        }
        url = f"{self.base_url}{cat.id}/"
        response = self.client.put(url, payload, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Updated C1"
        
        cat.refresh_from_db()
        assert cat.name == "Updated C1"

    def test_delete_category(self):
        cat = CategoryModel.objects.create(name="C1", description="D1", active=True)
        
        url = f"{self.base_url}{cat.id}/"
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        assert CategoryModel.objects.count() == 0
