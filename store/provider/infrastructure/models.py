from django.db import models
from core.models import ActivableModel
from core.models import BaseModel


class ProviderModel(BaseModel, ActivableModel):
    """
    Django ORM model for Provider.
    """

    name = models.CharField(max_length=255, null=False, blank=False)
    phone = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "providers"
        verbose_name = "Provider"
        verbose_name_plural = "Providers"
        app_label = "store"

    def __str__(self):
        return self.name
