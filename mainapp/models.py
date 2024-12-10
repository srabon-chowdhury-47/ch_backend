from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date

# # Room Table
class Room(models.Model):
    STATUS_CHOICES = [
        ('Vacant', 'Vacant'),
        ('Occupied', 'Occupied'),
        ('Needs clean', 'Needs clean'),
        ('Needs verify', 'Needs verify'),
        ('Locked','Locked'),
    ]
    
    ROOM_TYPE_CHOICES = [
        ('One Bed', 'One Bed'),
        ('Two Beds', 'Two Beds'),
    ]
    
    room_name = models.CharField(max_length=255)
    room_description=models.TextField(blank=True, null=True)
    room_type = models.CharField(max_length=10, choices=ROOM_TYPE_CHOICES)
    availability_status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    

    def __str__(self):
        return self.room_name


# # Guest Table
class Guest(models.Model):
    # Choices for user type
    USER_TYPE_CHOICES = [
        ('Government Officer', 'Government Officer'),
        ('Self-Government Officer', 'Self-Government Officer'),
        ('Private Sector Employee', 'Private Sector Employee'),
    ]
    
    nid = models.CharField(max_length=20, blank=True, null=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    motive_of_visiting = models.TextField(blank=True, null=True)
    total_person = models.IntegerField()
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    total_days = models.IntegerField(editable=False, null=True, blank=True)
    total_rental_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False, null=True, blank=True)
    signature = models.FileField(upload_to='signatures/', blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    user_type = models.CharField(max_length=30, choices=USER_TYPE_CHOICES, default='Government Officer')

    def save(self, *args, **kwargs):
        if self.check_in_date and self.check_out_date:
            self.total_days = (self.check_out_date - self.check_in_date).days
        
        # JSON structure for pricing
        pricing_data = {
            "Government Officer": {
                "One Bed": {
                    "1-3": 150,
                    "4-7": 200,
                    "8+": 450
                },
                "Two Beds": {
                    "1-3": 200,
                    "4-7": 250,
                    "8+": 750
                }
            },
            "Self-Government Officer": {
                "One Bed": {
                    "1-3": 200,
                    "4-7": 250,
                    "8+": 600
                },
                "Two Beds": {
                    "1-3": 300,
                    "4-7": 350,
                    "8+": 800
                }
            },
            "Private Sector Employee": {
                "One Bed": 1500,
                "Two Beds": 1800
            }
        }
        
        if self.room and self.user_type:
            room_type = self.room.room_type
            user_type = self.user_type
            
            # Get pricing based on room type and user type
            pricing = pricing_data.get(user_type, {}).get(room_type)
            
            if pricing:
                total_cost = 0
                remaining_days = self.total_days
                
                if isinstance(pricing, dict):  # Government and self-government categories
                    for days_range, price in pricing.items():
                        # Parsing the range (e.g., '1-3')
                        min_days, max_days = map(int, days_range.split('-') if '-' in days_range else (days_range, days_range))
                        
                        if remaining_days <= 0:
                            break
                        
                        if remaining_days > max_days:
                            total_cost += price * (max_days - min_days + 1)
                            remaining_days -= (max_days - min_days + 1)
                        else:
                            total_cost += price * remaining_days
                            remaining_days = 0
                
                else:  # Fixed price for Private Sector Employees (No range)
                    total_cost = pricing * self.total_days * self.total_person

                # Set the calculated total cost
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


