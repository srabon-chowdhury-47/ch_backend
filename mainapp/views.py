from django.shortcuts import render
from rest_framework import generics, viewsets, status
from .models import *
from .serializers import *
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from rest_framework.permissions import AllowAny, AllowAny
from rest_framework.decorators import api_view, permission_classes   # ✅ added
from rest_framework.response import Response
from django.template.loader import render_to_string
import datetime
from datetime import date


# ------------------- Room APIs -------------------
class RoomListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]  # Only authenticated users can access
    queryset = Room.objects.all()
    serializer_class = RoomSerializer


class RoomRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer


# ------------------- Pricing APIs -------------------
class PricingViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]  # Only authenticated users can access
    queryset = Pricing.objects.all()
    serializer_class = PriceSerializer


# ------------------- Booking APIs -------------------
class BookAPIView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = BookSerializer

    def get_queryset(self):
        return Guest.objects.exclude(
            id__in=CheckoutSummary.objects.values_list('guest_id', flat=True)
        )

    def perform_create(self, serializer):
        guest = serializer.save()
        room = guest.room
        room.availability_status = 'Booked'
        room.save()

        # Send confirmation email
        self.send_confirmation_email(guest)

    def send_confirmation_email(self, guest):
        context = {
            'guest': guest,
            'current_time': datetime.datetime.now()
        }

        html_content = render_to_string('Home/email_msg.html', context)
        subject = "Room Booking Confirmation"
        text_content = f"""
        Dear {guest.name},

        Your room booking at the Circuit House is confirmed. We look forward to hosting you.

        Best regards,
        Circuit House Management
        {datetime.datetime.now()}
        """

        from_email = settings.EMAIL_HOST_USER
        recipient_list = [guest.email]
        msg = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
        msg.attach_alternative(html_content, "text/html")
        msg.send()


class BookRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [AllowAny]
    queryset = Guest.objects.all()
    serializer_class = BookSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        previous_room = instance.room

        response = super().update(request, *args, **kwargs)

        updated_guest = self.get_object()
        updated_room = updated_guest.room

        if previous_room and previous_room != updated_room:
            previous_room.availability_status = 'Vacant'
            previous_room.save()

        if updated_room:
            updated_room.availability_status = 'Booked'
            updated_room.save()

        return response


# ------------------- Checkout APIs -------------------
class CheckOutView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    queryset = CheckoutSummary.objects.all().order_by('-created_at')
    serializer_class = CheckoutSummarySerializer

    def create(self, request, *args, **kwargs):
        try:
            guest_id = request.data.get("guest_id")
            payment_status = request.data.get("paymentStatus")
            bill_by = request.data.get("username")

            guest = Guest.objects.get(id=guest_id)

            # Create CheckoutSummary instance
            checkout_summary = CheckoutSummary.objects.create(
                guest=guest,
                payment_status=payment_status,
                bill_by=bill_by
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
        room.availability_status = 'Needs Housekeeping'
        room.save()

        # Send checkout confirmation email
        self.send_confirmation_email(guest)

    def send_confirmation_email(self, guest):
        context = {
            'guest': guest,
            'current_time': datetime.datetime.now()
        }

        html_content = render_to_string('Home/checkout_email.html', context)
        subject = "Checkout Confirmation"
        text_content = f"""
        Dear {guest.name},

        Your checkout from the Circuit House has been processed successfully.

        Best regards,
        Circuit House Management
        {datetime.datetime.now()}
        """

        from_email = settings.EMAIL_HOST_USER
        recipient_list = [guest.email]
        msg = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
        msg.attach_alternative(html_content, "text/html")
        msg.send()


# ------------------- Food Order APIs -------------------
class FoodOrderAPIView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    queryset = Food.objects.all()
    serializer_class = FoodSerializer

    def perform_create(self, serializer):
        serializer.save(date=date.today())


# ------------------- Other Cost APIs -------------------
class OtherCostAPIView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    queryset = OtherCost.objects.all()
    serializer_class = OtherCostSerializer

    def perform_create(self, serializer):
        serializer.save(date=date.today())


# ------------------- Public Guest Bill API -------------------
@api_view(['GET'])
@permission_classes([AllowAny])  # public access
def GuestBillView(request, nid):
    try:
        guest = Guest.objects.get(nid=nid)
        checkout = CheckoutSummary.objects.filter(guest=guest).last()

        guest_data = BookSerializer(guest).data
        if checkout:
            checkout_data = CheckoutSummarySerializer(checkout).data
        else:
            checkout_data = {"message": "Checkout not completed yet."}

        return Response({
            "guest": guest_data,
            "bill": checkout_data
        }, status=status.HTTP_200_OK)

    except Guest.DoesNotExist:
        return Response({"error": "No guest found with this NID."}, status=status.HTTP_404_NOT_FOUND)
