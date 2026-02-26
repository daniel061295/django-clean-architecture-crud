from django.urls import path
from .interfaces.views import HistoryListView, HistoryDetailView

urlpatterns = [
    path('', HistoryListView.as_view(), name='history-list'),
    path('<str:id>/', HistoryDetailView.as_view(), name='history-detail'),
]
