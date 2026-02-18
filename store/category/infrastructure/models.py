from django.db import models
from core.models import ActivableModel
from core.models import BaseModel

class CategoryModel(BaseModel, ActivableModel):
    """
    Django ORM model for Category.
    """
    name = models.CharField(max_length=255, unique=True, null=False, blank=False)
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "categories"
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        app_label = "store"

    def __str__(self):
        return self.name
