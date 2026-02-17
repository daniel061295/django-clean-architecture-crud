import pytest
from uuid import UUID
from datetime import datetime
from store.category.domain.entities import Category

def test_create_category_success():
    """Test successful creation of a category."""
    name = "Electronics"
    description = "Gadgets and devices"
    
    category = Category.create(name, description)
    
    assert isinstance(category.id, UUID)
    assert category.name == name
    assert category.description == description
    assert category.active is True
    assert isinstance(category.created_at, datetime)
    assert isinstance(category.updated_at, datetime)

def test_create_category_empty_name_fails():
    """Test that creating a category with empty name fails."""
    with pytest.raises(ValueError, match="Category name cannot be empty"):
        Category.create("")

def test_update_category_success():
    """Test successful update of a category."""
    category = Category.create("Old Name", "Old Desc")
    original_updated_at = category.updated_at
    
    new_name = "New Name"
    new_desc = "New Desc"
    new_active = False
    
    category.update(name=new_name, description=new_desc, active=new_active)
    
    assert category.name == new_name
    assert category.description == new_desc
    assert category.active == new_active
    assert category.updated_at > original_updated_at

def test_update_category_partial():
    """Test partial update of a category."""
    category = Category.create("Old Name", "Old Desc")
    
    category.update(name="New Name")
    
    assert category.name == "New Name"
    assert category.description == "Old Desc"
    assert category.active is True

def test_update_category_empty_name_fails():
    """Test that updating a category with empty name fails."""
    category = Category.create("Valid Name")
    
    with pytest.raises(ValueError, match="Category name cannot be empty"):
        category.update(name="")
