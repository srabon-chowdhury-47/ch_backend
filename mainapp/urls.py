from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

pricing_list_create=PricingViewSet.as_view({'get': 'list', 'post': 'create'})
pricing_detail=PricingViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})

urlpatterns = [
    
    path('room/', RoomListCreateAPIView.as_view(), name='room-list'), 
    path('pricing/', pricing_list_create, name='pricing-list-create'),
    path('pricing/<int:pk>/', pricing_detail, name='pricing-detail'),
    path('book/',BookAPIView.as_view(),name ="book"),
    path('food/',FoodOrderAPIView.as_view(),name='food'),
    path('other-cost/',OtherCostAPIView.as_view(),name='others'),

]