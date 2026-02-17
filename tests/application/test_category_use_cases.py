import pytest
from uuid import uuid4
from store.category.domain.entities import Category
from store.category.application.use_cases.create_category import CreateCategory
from store.category.application.use_cases.get_category import GetCategory
from store.category.application.use_cases.list_categories import ListCategories
from store.category.application.use_cases.update_category import UpdateCategory
from store.category.application.use_cases.delete_category import DeleteCategory
from store.category.application.dtos import CreateCategoryDTO, UpdateCategoryDTO
from tests.fakes.fake_category_repository import FakeCategoryRepository

def test_create_category_use_case():
    repo = FakeCategoryRepository()
    use_case = CreateCategory(repo)
    
    dto = CreateCategoryDTO(name="New Cat", description="New Desc")
    result = use_case.execute(dto)
    
    assert result.name == "New Cat"
    assert result.description == "New Desc"
    assert repo.exists_by_name("New Cat")

def test_get_category_use_case_found():
    repo = FakeCategoryRepository()
    category = Category.create("Existing")
    repo.save(category)
    
    use_case = GetCategory(repo)
    result = use_case.execute(category.id)
    
    assert result.id == category.id
    assert result.name == "Existing"

def test_get_category_use_case_not_found():
    repo = FakeCategoryRepository()
    use_case = GetCategory(repo)
    
    category = use_case.execute(uuid4())
    assert category is None

def test_list_categories_use_case():
    repo = FakeCategoryRepository()
    repo.save(Category.create("Cat 1"))
    repo.save(Category.create("Cat 2"))
    repo.save(Category.create("Cat 3"))
    
    use_case = ListCategories(repo)
    # Fix: Provide filters argument
    results, count = use_case.execute(page=1, page_size=2, filters={})
    
    assert count == 3
    assert len(results) == 2
    assert results[0].name == "Cat 1"

def test_update_category_use_case_success():
    repo = FakeCategoryRepository()
    category = Category.create("Old Name")
    repo.save(category)
    
    use_case = UpdateCategory(repo)
    # Fix: Include ID in DTO
    dto = UpdateCategoryDTO(id=category.id, name="New Name")
    
    # Fix: correct signature execute(dto)
    result = use_case.execute(dto)
    
    assert result.name == "New Name"
    updated_in_repo = repo.get_by_id(category.id)
    assert updated_in_repo.name == "New Name"

def test_update_category_use_case_not_found():
    repo = FakeCategoryRepository()
    use_case = UpdateCategory(repo)
    # Fix: Include ID in DTO
    dto = UpdateCategoryDTO(id=uuid4(), name="New Name")
    
    with pytest.raises(ValueError, match="not found"):
        use_case.execute(dto)

def test_delete_category_use_case_success():
    repo = FakeCategoryRepository()
    category = Category.create("To Delete")
    repo.save(category)
    
    use_case = DeleteCategory(repo)
    use_case.execute(category.id)
    
    assert repo.get_by_id(category.id) is None

def test_delete_category_use_case_not_found():
    repo = FakeCategoryRepository()
    use_case = DeleteCategory(repo)
    
    with pytest.raises(ValueError, match="not found"):
        use_case.execute(uuid4())
