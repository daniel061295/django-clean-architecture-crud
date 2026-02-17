import pytest
from uuid import uuid4
from store.provider.domain.entities import Provider
from store.provider.infrastructure.repositories import DjangoProviderRepository

@pytest.mark.django_db
def test_provider_repository_crud():
    repo = DjangoProviderRepository()
    
    # Create
    provider = Provider.create("Test Prov", email="test@test.com")
    saved = repo.save(provider)
    assert saved.id == provider.id
    assert saved.name == "Test Prov"
    
    # Get by ID
    retrieved = repo.get_by_id(provider.id)
    assert retrieved is not None
    assert retrieved.id == provider.id
    assert retrieved.email == "test@test.com"
    
    # Exists by name
    assert repo.exists_by_name("Test Prov") is True
    assert repo.exists_by_name("Non Existent") is False
    
    # Update
    provider.update(name="Updated Prov")
    repo.save(provider)
    updated = repo.get_by_id(provider.id)
    assert updated.name == "Updated Prov"
    
    # Delete
    repo.delete(provider.id)
    assert repo.get_by_id(provider.id) is None

@pytest.mark.django_db
def test_provider_repository_list_filters():
    repo = DjangoProviderRepository()
    
    p1 = Provider.create("Alpha", email="a@test.com")
    p2 = Provider.create("Beta", email="b@test.com")
    p3 = Provider.create("Gamma", email="g@test.com")
    
    repo.save(p1)
    repo.save(p2)
    repo.save(p3)
    
    # List all
    results, count = repo.list(1, 10, {})
    assert len(results) >= 3
    
    # Filter by name
    results, count = repo.list(1, 10, {"name": "Alpha"})
    assert len(results) == 1
    assert results[0].name == "Alpha"
