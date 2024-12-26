from django.shortcuts import render
from rest_framework import generics,viewsets
from .models import *
from .serializers import *
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.permissions import AllowAny, IsAuthenticated
import datetime
from django.template.loader import render_to_string
from rest_framework import generics, status
from rest_framework.response import Response

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
        
        guest = serializer.save()
        room = guest.room  
        room.availability_status = 'Occupied'
        room.save()

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
        
class CheckOutView(generics.ListCreateAPIView):
    queryset = CheckoutSummary.objects.all()
    serializer_class = CheckoutSummarySerializer

    def create(self, request, *args, **kwargs):
        try:
            guest_id = request.data.get("guest_id")
            payment_status = request.data.get("paymentStatus")

            print(guest_id, payment_status) 

            guest = Guest.objects.get(id=guest_id)

            # Create CheckoutSummary instance
            checkout_summary = CheckoutSummary.objects.create(
                guest=guest,
                payment_status=payment_status,
            )

            self.perform_create(checkout_summary)

            serializer = self.get_serializer(checkout_summary)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Guest.DoesNotExist:
            return Response({"error": "Guest not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, checkout_summary):
        
        guest = checkout_summary.guest
        room = guest.room  
        room.availability_status = 'Needs clean'
        room.save()

        # Send a confirmation email
        self.send_confirmation_email(guest)
        

    def send_confirmation_email(self, guest):
        
        context = {
        'guest': guest,
        'current_time': datetime.datetime.now()
         }

        html_content = render_to_string(
            'Home/checkout_email.html',
            context
        )
        subject = "Checkout Confirmation"

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
