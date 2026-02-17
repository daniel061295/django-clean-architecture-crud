from django.db import models
import uuid
from store.sale.domain.entities import SaleStatus

class SaleModel(models.Model):
    """
    Django ORM model for Sale.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateTimeField()
    total = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=50, choices=[(tag.name, tag.value) for tag in SaleStatus])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sales"
        verbose_name = "Sale"
        verbose_name_plural = "Sales"
        app_label = "store"

    def __str__(self):
        return f"Sale {self.id} - {self.status}"

class SaleDetailModel(models.Model):
    """
    Django ORM model for SaleDetail.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sale = models.ForeignKey(SaleModel, on_delete=models.CASCADE, related_name="details")
    plant_item_id = models.UUIDField(null=False)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = "sale_details"
        verbose_name = "Sale Detail"
        verbose_name_plural = "Sale Details"
        app_label = "store"

    def __str__(self):
        return f"Detail for {self.sale.id} - Item {self.plant_item_id}"
