from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date

# Users Table
class User(AbstractUser):
    ROLE_CHOICES = [
        ('NDC', 'NDC'),
        ('Staff', 'Staff'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES,default='Staff',blank=True,null=True)
    is_approved = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='img/', blank=True, null=True)

    # Specify related_name to avoid reverse accessor clashes
    groups = models.ManyToManyField(
        'auth.Group', 
        related_name='custom_user_set',  # Change 'custom_user_set' to a suitable name
        blank=True
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission', 
        related_name='custom_user_permissions_set',  # Change 'custom_user_permissions_set' to a suitable name
        blank=True
    )

    def __str__(self):
        return self.username

class StaffProfile(models.Model):
    name = models.CharField(max_length=255)
    picture = models.ImageField(upload_to='img/')
    designation = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    joining_date = models.DateField()
    ending_date = models.DateField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)


# Honour Board
class HonourBoard(models.Model):
    TYPE_CHOICES = [
        ('DC', 'DC'),
        ('NDC', 'NDC'),
    ]
    name = models.CharField(max_length=255)
    batch = models.CharField(max_length=50)
    joining_date = models.DateField()
    ending_date = models.DateField(blank=True,null=True)
    photo = models.ImageField(upload_to='img/',blank=True,null=True)
    remarks = models.TextField(blank=True, null=True)
    designation_type = models.CharField(max_length=3, choices=TYPE_CHOICES, default='DC') 

    def __str__(self):
        return f"{self.name} - {self.designation_type}"