from store.provider.domain.entities import Provider
from store.provider.infrastructure.models import ProviderModel

class ProviderMapper:
    """
    Mapper between Provider domain entity and ProviderModel Django model.
    """

    @staticmethod
    def to_domain(model: ProviderModel) -> Provider:
        return Provider(
            id=model.id,
            name=model.name,
            phone=model.phone,
            email=model.email,
            address=model.address,
            active=model.active,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    @staticmethod
    def to_db(entity: Provider) -> ProviderModel:
        return ProviderModel(
            id=entity.id,
            name=entity.name,
            phone=entity.phone,
            email=entity.email,
            address=entity.address,
            active=entity.active,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )
