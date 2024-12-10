from .models import HonourBoard
from rest_framework import serializers

class HonourBoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = HonourBoard
        fields = '__all__'

    def validate(self, data):
        """
        Perform validation on ending_date and joining_date together.
        """
        joining_date = data.get('joining_date')
        ending_date = data.get('ending_date')

        if ending_date and joining_date and ending_date <= joining_date:
            raise serializers.ValidationError({
                "ending_date": "Ending date must be after the joining date."
            })

        return data
