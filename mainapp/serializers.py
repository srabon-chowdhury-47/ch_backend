from .models import *
from rest_framework import serializers

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'
        
    def validate(self, data):
        if data['availability_status'] == 'Vacant' and not data.get('room_type'):
            raise serializers.ValidationError("Room type is required when status is 'Vacant'.")
        return data
    
    def perform_create(self, serializer):
        try:
            serializer.save()
        except serializers.ValidationError as e:
            print(e.detail)  # Logs validation errors
            raise

class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pricing
        fields ='__all__'
    
    def validate_days(self,value):
        if self.initial_data.get('user_type') != 'Private Sector Employee' and not value:
            raise serializers.ValidationError("This field is required for the selected user type.")
        return value
    