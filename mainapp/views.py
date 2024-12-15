from django.shortcuts import render
from rest_framework import generics
from .models import Room
from .serializers import *
from rest_framework.permissions import AllowAny, IsAuthenticated

class RoomListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]  
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

    def get_permissions(self):
        """Override to set different permissions for GET and POST methods"""
        if self.request.method == 'POST':
            return [IsAuthenticated()]  # Only authenticated users can create rooms
        return [AllowAny()]  # Allow everyone to view rooms