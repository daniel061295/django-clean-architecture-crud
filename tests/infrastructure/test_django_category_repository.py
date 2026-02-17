import pytest
from uuid import uuid4
from store.category.domain.entities import Category
from store.category.infrastructure.repositories import DjangoCategoryRepository

@pytest.mark.django_db
def test_category_repository_crud():
    repo = DjangoCategoryRepository()
    
    # Create
    category = Category.create("Test Cat", "Desc")
    saved = repo.save(category)
    assert saved.id == category.id
    assert saved.name == "Test Cat"
    
    # Get by ID
    retrieved = repo.get_by_id(category.id)
    assert retrieved is not None
    assert retrieved.id == category.id
    assert retrieved.name == "Test Cat"
    
    # Exists by name
    assert repo.exists_by_name("Test Cat") is True
    assert repo.exists_by_name("Non Existent") is False
    
    # Update
    category.update(name="Updated Cat")
    repo.save(category)
    updated = repo.get_by_id(category.id)
    assert updated.name == "Updated Cat"
    
    # Delete
    repo.delete(category.id)
    assert repo.get_by_id(category.id) is None

@pytest.mark.django_db
def test_category_repository_list_filters():
    repo = DjangoCategoryRepository()
    
    c1 = Category.create("Apple", "Fruit")
    c2 = Category.create("Banana", "Fruit")
    c3 = Category.create("Carrot", "Veggie")
    
    repo.save(c1)
    repo.save(c2)
    repo.save(c3)
    
    # List all
    results, count = repo.list(1, 10, {})
    assert len(results) >= 3
    
    # Filter by name
    results, count = repo.list(1, 10, {"name": "Apple"})
    assert len(results) == 1
    assert results[0].name == "Apple"
    
    # Pagination
    results, count = repo.list(1, 1, {})
    assert len(results) == 1
