from django.db import models
from core.models import UUIDModel, TimeStampedModel


class PlantItemModel(UUIDModel, TimeStampedModel):
    """
    Django ORM model for storing PlantItems.

    Attributes:
        name (CharField): Name of the plant.
        description (TextField): Description.
        price (DecimalField): Price with max digits 10 and 2 decimal places.
        stock (IntegerField): Stock quantity.
        is_available (BooleanField): Availability status store for efficient querying.
    """

    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    # is_available is derived from stock in domain, but we can store it for easier querying or calculate it.
    # The requirement says "is_available debe depender del stock".
    # Let's simple store it to match the entity and query efficiently.
    is_available = models.BooleanField(default=False)

    class Meta:
        db_table = "plant_items"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
