import pytest
from uuid import UUID
from datetime import datetime
from store.provider.domain.entities import Provider

def test_create_provider_success():
    """Test successful creation of a provider."""
    name = "Tech Supplier Inc."
    email = "contact@techsupplier.com"
    phone = "123-456-7890"
    address = "123 Tech Blvd"
    
    provider = Provider.create(name, phone, email, address)
    
    assert isinstance(provider.id, UUID)
    assert provider.name == name
    assert provider.email == email
    assert provider.phone == phone
    assert provider.address == address
    assert provider.active is True
    assert isinstance(provider.created_at, datetime)
    assert isinstance(provider.updated_at, datetime)

def test_create_provider_empty_name_fails():
    """Test that creating a provider with empty name fails."""
    with pytest.raises(ValueError, match="Provider name cannot be empty"):
        Provider.create("")

def test_create_provider_invalid_email_fails():
    """Test that creating a provider with invalid email fails."""
    with pytest.raises(ValueError, match="Invalid email format"):
        Provider.create("Name", email="invalid-email")

def test_update_provider_success():
    """Test successful update of a provider."""
    provider = Provider.create("Old Name", email="old@example.com")
    original_updated_at = provider.updated_at
    
    new_name = "New Name"
    new_email = "new@example.com"
    new_active = False
    
    provider.update(name=new_name, email=new_email, active=new_active)
    
    assert provider.name == new_name
    assert provider.email == new_email
    assert provider.active == new_active
    # In some fast execution environments, create and update might happen in same microsecond potentially.
    # But usually datetime precision captures it.
    assert provider.updated_at >= original_updated_at 

def test_update_provider_partial():
    """Test partial update of a provider."""
    provider = Provider.create("Old Name", email="old@example.com")
    
    provider.update(name="New Name")
    
    assert provider.name == "New Name"
    assert provider.email == "old@example.com"

def test_update_provider_empty_name_fails():
    """Test that updating a provider to empty name fails."""
    provider = Provider.create("Valid Name")
    
    with pytest.raises(ValueError, match="Provider name cannot be empty"):
        provider.update(name="")

def test_update_provider_invalid_email_fails():
    """Test that updating a provider to invalid email fails."""
    provider = Provider.create("Valid Name")
    
    with pytest.raises(ValueError, match="Invalid email format"):
        provider.update(email="invalid-email")
