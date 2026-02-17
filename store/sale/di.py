from injector import Module, provider, singleton
from store.sale.domain.repositories import SaleRepository
from store.sale.infrastructure.repositories import DjangoSaleRepository
from store.sale.application.use_cases.create_sale import CreateSale
from store.sale.application.use_cases.add_sale_detail import AddSaleDetail
from store.sale.application.use_cases.complete_sale import CompleteSale
from store.sale.application.use_cases.list_sales import ListSales
from store.sale.application.use_cases.get_sale import GetSale
from store.inventory_movement.application.use_cases.register_inventory_movement import RegisterInventoryMovement

class SaleModule(Module):
    @provider
    @singleton
    def provide_repository(self) -> SaleRepository:
        return DjangoSaleRepository()

    @provider
    def provide_create_sale(self, repository: SaleRepository) -> CreateSale:
        return CreateSale(repository)

    @provider
    def provide_add_sale_detail(self, repository: SaleRepository) -> AddSaleDetail:
        return AddSaleDetail(repository)

    @provider
    def provide_complete_sale(self, repository: SaleRepository, inventory_use_case: RegisterInventoryMovement) -> CompleteSale:
        return CompleteSale(repository, inventory_use_case)

    @provider
    def provide_list_sales(self, repository: SaleRepository) -> ListSales:
        return ListSales(repository)

    @provider
    def provide_get_sale(self, repository: SaleRepository) -> GetSale:
        return GetSale(repository)
