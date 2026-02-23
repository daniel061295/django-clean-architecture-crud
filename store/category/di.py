from injector import Module, provider, singleton
from store.category.domain.repositories import CategoryRepository
from store.category.infrastructure.repositories import DjangoCategoryRepository, DynamoDBCategoryRepository
from store.category.application.use_cases.create_category import CreateCategory
from store.category.application.use_cases.list_categories import ListCategories
from store.category.application.use_cases.get_category import GetCategory
from store.category.application.use_cases.update_category import UpdateCategory
from store.category.application.use_cases.delete_category import DeleteCategory

class CategoryModule(Module):
    @provider
    @singleton
    def provide_repository(self) -> CategoryRepository:
        return DynamoDBCategoryRepository()

    @provider
    def provide_create_category(self, repository: CategoryRepository) -> CreateCategory:
        return CreateCategory(repository)

    @provider
    def provide_list_categories(self, repository: CategoryRepository) -> ListCategories:
        return ListCategories(repository)

    @provider
    def provide_get_category(self, repository: CategoryRepository) -> GetCategory:
        return GetCategory(repository)

    @provider
    def provide_update_category(self, repository: CategoryRepository) -> UpdateCategory:
        return UpdateCategory(repository)

    @provider
    def provide_delete_category(self, repository: CategoryRepository) -> DeleteCategory:
        return DeleteCategory(repository)
