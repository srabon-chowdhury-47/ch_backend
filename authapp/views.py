from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework import status
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from .models import HonourBoard
from .serializers import*
from rest_framework.permissions import BasePermission
User=get_user_model()
from rest_framework.permissions import IsAuthenticated


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        print(f"User Role: {request.user.role}")  # Debugging output to check the role of the user
        return request.user.is_authenticated and request.user.role == 'NDC'


# List and Create HonourBoard entries
class HonourBoardListCreateView(generics.ListCreateAPIView):
    queryset = HonourBoard.objects.all()
    serializer_class = HonourBoardSerializer

# Retrieve, Update, and Delete a specific HonourBoard entry
class HonourBoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = HonourBoard.objects.all()
    serializer_class = HonourBoardSerializer

class UserRegistrationView(generics.CreateAPIView):
    serializer_class=UserRegistrationSerializer

class StaffListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = StaffApproveSerializer

class StaffApproveView(generics.UpdateAPIView):
    permission_classes = [IsAdmin] 
    queryset = User.objects.all()
    serializer_class = StaffApproveSerializer

    def update(self, request, *args, **kwargs):
        user = self.get_object()  # Get the specific User instance
        user.is_approved = request.data.get('is_approved', user.is_approved)  # Update is_approved field
        user.save()  # Save the updated user instance
        return Response({"message": f"User {user.username} approval status updated successfully."}, status=status.HTTP_200_OK)
    def delete(self,request,*args,**kwargs):
        try:
            user=self.get_object()
            user.delete()
            return Response({"message": f"User deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response({"error":"User doesn't exist"},status=status.HTTP_404_NOT_FOUND )

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class PasswordChangeView(APIView):
    permission_classes=[IsAuthenticated]

    def post(self, request):
            serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                # Change password logic
                request.user.set_password(serializer.validated_data['new_password'])
                request.user.save()
                return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)