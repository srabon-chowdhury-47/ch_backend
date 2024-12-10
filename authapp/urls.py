from django.urls import path
from .views import *

urlpatterns = [
    path('honour-board/', HonourBoardListCreateView.as_view(), name='honourboard-list-create'),
    
    # Retrieve, update, or delete a specific HonourBoard entry by ID
    path('honour-board/<int:pk>/', HonourBoardDetailView.as_view(), name='honourboard-detail'),
]