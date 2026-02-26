import pytest
from rest_framework.test import APIClient
from rest_framework import status
from store.tips.infrastructure.models import TipModel

@pytest.mark.django_db
class TestTipAPI:
    def setup_method(self):
        self.client = APIClient()
        self.base_url = "/api/tips/"

    def test_random_tip(self):
        TipModel.objects.create(title="Tip 1", description="Desc 1", icon="icon1")
        TipModel.objects.create(title="Tip 2", description="Desc 2", icon="icon2")
        
        response = self.client.get(f"{self.base_url}random/")
        assert response.status_code == status.HTTP_200_OK
        assert "id" in response.data
        assert response.data["title"] in ["Tip 1", "Tip 2"]

    def test_random_tip_empty(self):
        response = self.client.get(f"{self.base_url}random/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_random_tip_consecutive_not_same(self):
        TipModel.objects.create(title="Tip 1", description="Desc 1", icon="icon1")
        TipModel.objects.create(title="Tip 2", description="Desc 2", icon="icon2")
        
        # 1st call
        response1 = self.client.get(f"{self.base_url}random/")
        assert response1.status_code == status.HTTP_200_OK
        tip1_id = response1.data["id"]

        # 2nd call
        response2 = self.client.get(f"{self.base_url}random/")
        assert response2.status_code == status.HTTP_200_OK
        tip2_id = response2.data["id"]

        assert tip1_id != tip2_id
