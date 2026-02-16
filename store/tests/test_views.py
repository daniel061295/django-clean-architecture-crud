from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from store.domain.entities import PlantItem
from store.infrastructure.repositories import DjangoPlantItemRepository
from decimal import Decimal


class PlantItemViewTestCase(APITestCase):
    def setUp(self):
        self.repository = DjangoPlantItemRepository()
        self.list_url = reverse("plant-items-list")
        self.detail_url = lambda pk: reverse("plant-items-detail", args=[pk])
        self.item_data = {
            "name": "View Plant",
            "description": "View Desc",
            "price": "15.50",
            "stock": 10,
        }

    def test_create_item_success(self):
        response = self.client.post(self.list_url, self.item_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], self.item_data["name"])
        self.assertIn("id", response.data)

    def test_create_item_invalid(self):
        # Missing required field
        invalid_data = {"name": "Incomplete"}
        response = self.client.post(self.list_url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_item_domain_error(self):
        # Negative price triggers DomainError
        invalid_data = self.item_data.copy()
        invalid_data["price"] = "-10.00"
        response = self.client.post(self.list_url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Verify it's a domain error message
        self.assertIn("error", response.data)

    def test_list_items(self):
        # Create a few items first
        self.client.post(self.list_url, self.item_data)
        self.client.post(self.list_url, self.item_data)

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data["items"]) >= 2)

    def test_get_item_success(self):
        create_response = self.client.post(self.list_url, self.item_data)
        item_id = create_response.data["id"]

        response = self.client.get(self.detail_url(item_id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], item_id)

    def test_get_item_not_found(self):
        # Random UUID
        import uuid

        random_id = uuid.uuid4()
        response = self.client.get(self.detail_url(random_id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_item_invalid_uuid(self):
        # Invalid UUID format
        response = self.client.get(self.detail_url("invalid-uuid"))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_item(self):
        create_response = self.client.post(self.list_url, self.item_data)
        item_id = create_response.data["id"]

        update_data = self.item_data.copy()
        update_data["name"] = "Updated View Plant"

        response = self.client.put(self.detail_url(item_id), update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Updated View Plant")

    def test_delete_item(self):
        create_response = self.client.post(self.list_url, self.item_data)
        item_id = create_response.data["id"]

        response = self.client.delete(self.detail_url(item_id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify it's gone
        get_response = self.client.get(self.detail_url(item_id))
        self.assertEqual(get_response.status_code, status.HTTP_404_NOT_FOUND)
