from django.urls import path
from .views import *

urlpatterns = [
    path('honour-board/', HonourBoardListCreateView.as_view(), name='honourboard-list-create'),
    # Retrieve, update, or delete a specific HonourBoard entry by ID
    path('honour-board/<int:pk>/', HonourBoardDetailView.as_view(), name='honourboard-detail'),
    path('register/',UserRegistrationView.as_view(),name='register'),
    path('approve_staff/', StaffListCreateView.as_view(), name='approve_staff'),
    path('approve_staff/<int:pk>/', StaffApproveView.as_view(), name='approve_staff'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('change-password/',PasswordChangeView.as_view(),name='change-password'),
    path('user/', UserProfileView.as_view(), name='user-profile')
]