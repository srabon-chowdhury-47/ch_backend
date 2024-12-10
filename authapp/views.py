from rest_framework import generics
from .models import HonourBoard
from .serializers import HonourBoardSerializer

# List and Create HonourBoard entries
class HonourBoardListCreateView(generics.ListCreateAPIView):
    queryset = HonourBoard.objects.all()
    serializer_class = HonourBoardSerializer

# Retrieve, Update, and Delete a specific HonourBoard entry
class HonourBoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = HonourBoard.objects.all()
    serializer_class = HonourBoardSerializer
