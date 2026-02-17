from store.category.domain.entities import Category
from store.category.infrastructure.models import CategoryModel

class CategoryMapper:
    """
    Mapper between Category domain entity and CategoryModel Django model.
    """

    @staticmethod
    def to_domain(model: CategoryModel) -> Category:
        """
        Converts a CategoryModel to a Category domain entity.

        Args:
            model: CategoryModel to convert.

        Returns:
            Category domain entity.
        """
        return Category(
            id=model.id,
            name=model.name,
            description=model.description,
            active=model.active,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    @staticmethod
    def to_db(entity: Category) -> CategoryModel:
        """
        Converts a Category domain entity to a CategoryModel Django model.

        Args:
            entity: Category domain entity to convert.

        Returns:
            CategoryModel Django model.
        """
        return CategoryModel(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            active=entity.active,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )
