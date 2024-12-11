from django.shortcuts import render
from rest_framework import generics
from .models import Room
from .serializers import *

class RoomListCreateAPIView(generics.ListCreateAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer


