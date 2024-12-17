from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date

from django.db import models
from datetime import date




# Room Table
class Room(models.Model):
    STATUS_CHOICES = [
        ('Vacant', 'Vacant'),
        ('Occupied', 'Occupied'),
        ('Needs clean', 'Needs clean'),
        ('Needs verify', 'Needs verify'),
        ('Locked', 'Locked'),
    ]
    
    ROOM_TYPE_CHOICES = [
        ('One Bed', 'One Bed'),
        ('Two Beds', 'Two Beds'),
    ]
    
    room_name = models.CharField(max_length=255)
    room_description = models.TextField(blank=True, null=True)
    room_type = models.CharField(max_length=10, choices=ROOM_TYPE_CHOICES)
    availability_status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    
    def __str__(self):
        return self.room_name
        # Pricing Table

class Pricing(models.Model):
    USER_TYPE_CHOICES = [
        ('Government Officer', 'Government Officer'),
        ('Self-Government Officer', 'Self-Government Officer'),
        ('Private Sector Employee', 'Private Sector Employee'),
    ]
    
    ROOM_TYPE_CHOICES = [
        ('One Bed', 'One Bed'),
        ('Two Beds', 'Two Beds'),
    ]
    
    user_type = models.CharField(max_length=30, choices=USER_TYPE_CHOICES)
    room_type = models.CharField(max_length=10, choices=ROOM_TYPE_CHOICES)
    days_range = models.CharField(max_length=10, blank=True, null=True, help_text="e.g., 1-3, 4-7, or 7+")
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        unique_together = ('user_type', 'room_type', 'days_range')
    
    def __str__(self):
        return f"{self.user_type} , {self.room_type} , {self.days_range}: {self.price_per_day}"


# Guest Table
class Guest(models.Model):
    USER_TYPE_CHOICES = [
        ('Government Officer', 'Government Officer'),
        ('Self-Government Officer', 'Self-Government Officer'),
        ('Private Sector Employee', 'Private Sector Employee'),
    ]
    
    nid = models.CharField(max_length=20, blank=True, null=True)
    designation=models.CharField(max_length=50, blank=True, null=True)
    user_type = models.CharField(max_length=30, choices=USER_TYPE_CHOICES, default='Government Officer')
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    motive_of_visiting = models.TextField(blank=True, null=True)
    total_person = models.IntegerField()
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    total_days = models.IntegerField(editable=False, null=True, blank=True)
    total_rental_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False, null=True, blank=True)
    comment = models.TextField(blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if self.check_in_date and self.check_out_date:
            self.total_days = (self.check_out_date - self.check_in_date).days

        # Calculate rental price based on Pricing table
        if self.room and self.user_type:
            room_type = self.room.room_type
            user_type = self.user_type

            pricing_entries = Pricing.objects.filter(user_type=user_type, room_type=room_type).order_by('days_range')
            total_cost = 0
            remaining_days = self.total_days

            for pricing in pricing_entries:
                days_range = pricing.days_range
                price_per_day = pricing.price_per_day

                # Check for flat pricing (e.g., 1500 taka per day)
                if '+' not in days_range and '-' not in days_range:
                    total_cost += price_per_day * remaining_days
                    remaining_days = 0
                    break

                # Handle ranged pricing like '1-3' or '4-7'
                if '-' in days_range:
                    min_days, max_days = map(int, days_range.split('-'))
                else:  # Handle open-ended ranges like '7+'
                    min_days = int(days_range.rstrip('+'))
                    max_days = float('inf')

                if remaining_days <= 0:
                    break

                if min_days <= self.total_days <= max_days:  # Current total_days fits the range
                    days_in_range = min(remaining_days, max_days - min_days + 1)
                    total_cost += price_per_day * days_in_range
                    remaining_days -= days_in_range
                elif remaining_days > 0 and max_days == float('inf'):  # For '7+' type ranges
                    total_cost += price_per_day * remaining_days
                    remaining_days = 0

            self.total_rental_price = total_cost

        super(Guest, self).save(*args, **kwargs)

    
    def __str__(self):
        return self.name



# Food Table
class Food(models.Model):
    TIME_CHOICES = [
        ('Breakfast', 'Breakfast'),
        ('Launch', 'Launch'),
        ('Dinner', 'Dinner'),
    ]
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE)
    date = models.DateField()
    food_menu = models.TextField()
    Order_time = models.CharField(max_length=20, choices=TIME_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

class OtherCost(models.Model):
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE)
    items = models.CharField(max_length=50)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    date_added = models.DateField(default=date.today)
    
    def __str__(self):
        return f"{self.item} - {self.cost} ({self.date_added})"


# Checkout Summary Table
class CheckoutSummary(models.Model):
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE)
    total_rental_cost = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    total_food_cost = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    total_other_cost = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    payment_status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Completed', 'Completed')], default='Pending')
    payment_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Calculate total costs
        self.total_rental_cost = self.guest.total_rental_price
        self.total_food_cost = sum([food.price for food in Food.objects.filter(guest=self.guest)])  # Assuming the food cost is stored in the Food model
        self.total_other_cost = sum([cost.cost for cost in OtherCost.objects.filter(guest=self.guest)])
        
        # Calculate the grand total including the other cost
        self.grand_total = self.total_rental_cost + self.total_food_cost + self.total_other_cost
        super(CheckoutSummary, self).save(*args, **kwargs)


