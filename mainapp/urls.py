from django.urls import path
from .views import *

pricing_list_create=PricingViewSet.as_view({'get': 'list', 'post': 'create'})
pricing_detail=PricingViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})

urlpatterns = [
    
    path('room/', RoomListCreateAPIView.as_view(), name='room-list'), 
    path('pricing/', pricing_list_create, name='pricing-list-create'),
    path('pricing/<int:pk>/', pricing_detail, name='pricing-detail'),
    path('book/',BookAPIView.as_view(),name ="book")
]