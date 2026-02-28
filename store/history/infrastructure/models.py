from django.db import models
from django.conf import settings
import uuid

class HistoryModel(models.Model):
    """
    Django ORM Model for History Entity
    """
    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="histories",
        null=True,
        blank=True
    )
    is_healthy = models.BooleanField()
    title = models.CharField(max_length=255, default='Diagnóstico Múltiple')
    diagnosis = models.CharField(max_length=255)
    confidence = models.FloatField()
    treatment = models.JSONField(default=list)
    urgency_level = models.CharField(max_length=50)
    photo = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'history'
        verbose_name = 'History'
        verbose_name_plural = 'Histories'

    def __str__(self):
        return f"History {self.id} - {self.diagnosis}"
