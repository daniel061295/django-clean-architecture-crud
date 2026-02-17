import pytest
from uuid import uuid4
from store.provider.domain.entities import Provider
from store.provider.application.use_cases.create_provider import CreateProvider
from store.provider.application.use_cases.get_provider import GetProvider
from store.provider.application.use_cases.list_providers import ListProviders
from store.provider.application.use_cases.update_provider import UpdateProvider
from store.provider.application.use_cases.delete_provider import DeleteProvider
from store.provider.application.dtos import CreateProviderDTO, UpdateProviderDTO
from tests.fakes.fake_provider_repository import FakeProviderRepository

def test_create_provider_use_case():
    repo = FakeProviderRepository()
    use_case = CreateProvider(repo)
    
    dto = CreateProviderDTO(name="New Prov", email="test@test.com", phone="123", address="Addr")
    result = use_case.execute(dto)
    
    assert result.name == "New Prov"
    assert result.email == "test@test.com"
    assert repo.exists_by_name("New Prov")
    assert repo.exists_by_email("test@test.com")

def test_get_provider_use_case_found():
    repo = FakeProviderRepository()
    provider = Provider.create("Existing")
    repo.save(provider)
    
    use_case = GetProvider(repo)
    result = use_case.execute(provider.id)
    
    assert result.id == provider.id
    assert result.name == "Existing"

def test_get_provider_use_case_not_found():
    repo = FakeProviderRepository()
    use_case = GetProvider(repo)
    
    provider = use_case.execute(uuid4())
    assert provider is None

def test_list_providers_use_case():
    repo = FakeProviderRepository()
    repo.save(Provider.create("Prov 1"))
    repo.save(Provider.create("Prov 2"))
    repo.save(Provider.create("Prov 3"))
    
    use_case = ListProviders(repo)
    results, count = use_case.execute(page=1, page_size=2, filters={})
    
    assert count == 3
    assert len(results) == 2
    assert results[0].name == "Prov 1"

def test_update_provider_use_case_success():
    repo = FakeProviderRepository()
    provider = Provider.create("Old Name", email="old@test.com")
    repo.save(provider)
    
    use_case = UpdateProvider(repo)
    dto = UpdateProviderDTO(id=provider.id, name="New Name")
    
    result = use_case.execute(dto)
    
    assert result.name == "New Name"
    updated_in_repo = repo.get_by_id(provider.id)
    assert updated_in_repo.name == "New Name"

def test_update_provider_use_case_not_found():
    repo = FakeProviderRepository()
    use_case = UpdateProvider(repo)
    dto = UpdateProviderDTO(id=uuid4(), name="New Name")
    
    with pytest.raises(ValueError, match="not found"):
        use_case.execute(dto)

def test_delete_provider_use_case_success():
    repo = FakeProviderRepository()
    provider = Provider.create("To Delete")
    repo.save(provider)
    
    use_case = DeleteProvider(repo)
    use_case.execute(provider.id)
    
    assert repo.get_by_id(provider.id) is None

def test_delete_provider_use_case_not_found():
    repo = FakeProviderRepository()
    use_case = DeleteProvider(repo)
    
    with pytest.raises(ValueError, match="not found"):
        use_case.execute(uuid4())
