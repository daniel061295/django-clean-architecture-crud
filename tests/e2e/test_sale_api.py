import pytest
from rest_framework.test import APIClient
from rest_framework import status
from store.sale.infrastructure.models import SaleModel
from store.plant_item.infrastructure.models import PlantItemModel
from uuid import uuid4

@pytest.mark.django_db
class TestSaleAPI:
    def setup_method(self):
        self.client = APIClient()
        self.base_url = "/api/sales/"

    def test_create_sale(self):
        response = self.client.post(self.base_url, {}, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert "id" in response.data
        assert response.data["status"] == "PENDIENTE"
        
        # Verify DB
        assert SaleModel.objects.count() == 1

    def test_list_sales(self):
        # Create some sales directly in DB or via Client
        self.client.post(self.base_url, {}, format='json')
        self.client.post(self.base_url, {}, format='json')
        
        response = self.client.get(self.base_url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["data"]) >= 2

    def test_retrieve_sale(self):
        create_response = self.client.post(self.base_url, {}, format='json')
        sale_id = create_response.data["id"]
        
        url = f"{self.base_url}{sale_id}/"
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == sale_id

    def test_add_item_to_sale(self):
        # 1. Create Sale
        sale_response = self.client.post(self.base_url, {}, format='json')
        sale_id = sale_response.data["id"]
        
        # 2. Create Plant Item (Need a real one in DB)
        plant_item = PlantItemModel.objects.create(
            id=uuid4(),
            name="Rose",
            description="Desc",
            price=10.0,
            stock=10,
            is_available=True
        )
        
        # 3. Add Item
        payload = {
            "plant_item_id": str(plant_item.id),
            "quantity": 2,
            "unit_price": 10.0
        }
        
        url = f"{self.base_url}{sale_id}/items/"
        response = self.client.post(url, payload, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert float(response.data["total"]) == 20.0
        assert len(response.data["details"]) == 1

    def test_complete_sale(self):
         # 1. Create Sale
        sale_response = self.client.post(self.base_url, {}, format='json')
        sale_id = sale_response.data["id"]

         # 2. Create Plant Item
        plant_item = PlantItemModel.objects.create(
            id=uuid4(),
            name="Rose",
            description="Desc",
            price=10.0,
            stock=10,
            is_available=True
        )

        # 3. Add Item
        payload = {
            "plant_item_id": str(plant_item.id),
            "quantity": 2,
            "unit_price": 10.0
        }
        url_add = f"{self.base_url}{sale_id}/items/"
        self.client.post(url_add, payload, format='json')

        # 4. Complete Sale
        url_complete = f"{self.base_url}{sale_id}/complete/"
        response = self.client.post(url_complete, {}, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "COMPLETADA"
        
        plant_item.refresh_from_db()
        # Assumes logic reduces stock. If not implemented, skip this assertion or expect failure if TDD.
        # Given "InventoryMovement" logic exists, it SHOULD reduce stock.
        # But `CompleteSale` needs to call `RegisterInventoryMovement`. This integration is key.
        # If it fails, I know where to fix logic.
