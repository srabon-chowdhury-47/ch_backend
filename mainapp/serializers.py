from .models import Room
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