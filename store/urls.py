from django.urls import path
from store.interfaces.views import PlantItemView, PlantItemDetailView

urlpatterns = [
    path('plant-items/', PlantItemView.as_view(), name='plant-items-list-create'),
    path('plant-items/<uuid:item_id>/', PlantItemDetailView.as_view(), name='plant-items-detail'),
]
