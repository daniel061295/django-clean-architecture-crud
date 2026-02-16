import uuid
from django.db import models


class UUIDModel(models.Model):
    """
    Abstract base model that uses a UUID as the primary key.

    Attributes:
        id (UUIDField): The primary key, automatically generated using uuid4.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class TimeStampedModel(models.Model):
    """
    Abstract base model that adds created_at and updated_at fields.

    Attributes:
        created_at (DateTimeField): The timestamp when the object was created.
        updated_at (DateTimeField): The timestamp when the object was last updated.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
