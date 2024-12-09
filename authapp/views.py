from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render

@api_view(['GET'])
def hello_world(request):
    return Response({"message": "Hello, React! I am Joydip"})


def home(request):
    return render(request, 'Home/home.html')
