from django.shortcuts import render
from rest_framework import generics,viewsets
from .models import *
from .serializers import *
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.permissions import AllowAny, IsAuthenticated
import datetime
from django.template.loader import render_to_string

class RoomListCreateAPIView(generics.ListCreateAPIView):
    # permission_classes = [IsAuthenticated]  # Only authenticated users can access
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

    def get_permissions(self):
        """Override to set different permissions for GET and POST methods"""
        if self.request.method == 'POST':
            return [IsAuthenticated()]  # Only authenticated users can create rooms
        return [AllowAny()]  # Allow everyone to view rooms


class PricingViewSet(viewsets.ModelViewSet):
    # permission_classes = [IsAuthenticated]  # Only authenticated users can access
    queryset = Pricing.objects.all()
    serializer_class = PriceSerializer
    
from django.core.mail import EmailMultiAlternatives 
class BookAPIView(generics.ListCreateAPIView):
    # permission_classes = [IsAuthenticated]  # Only authenticated users can access

    permission_classes = [AllowAny]  
    queryset = Guest.objects.filter()
    serializer_class = BookSerializer
    
    def perform_create(self, serializer):
        # Save the new booking
        guest = serializer.save()

        # Send a confirmation email
        self.send_confirmation_email(guest)
        

    def send_confirmation_email(self, guest):
        
        context = {
        'guest': guest,
        'current_time': datetime.datetime.now()
         }

        html_content = render_to_string(
            'Home/email_msg.html',
            context
        )
        subject = "Room Booking Confirmation"
        text_content = f"""
        Dear {guest.name},\n\n" "Your room booking at the Circuit House is confirmed. We look forward to hosting you.
        \n\n" "Best regards,\nCircuit House Management"
        {datetime.datetime.now()}
        """
        
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [guest.email]
        msg = EmailMultiAlternatives(subject, text_content, from_email,recipient_list)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        # send_mail(
        #     subject,
        #     message,
        #     settings.EMAIL_HOST_USER,
        #     recipient_list,
        #     fail_silently=False,
        # )

class FoodOrderAPIView(generics.ListCreateAPIView):
    # permission_classes = [IsAuthenticated]  # Only authenticated users can access

    queryset = Food.objects.all()
    serializer_class = FoodSerializer

    def perform_create(self, serializer):
        serializer.save(date=date.today())  # Automatically set the current date

class OtherCostAPIView(generics.ListCreateAPIView):
    # permission_classes = [IsAuthenticated]  # Only authenticated users can access

    queryset = OtherCost.objects.all()
    serializer_class = OtherCostSerializer
    # permission_classes = [IsAuthenticated]  # Require authentication for ordering food

    def perform_create(self, serializer):
        serializer.save(date=date.today())  # Automatically set the current date
