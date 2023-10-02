from rest_framework import serializers
from elevator.models import Elevator, ElevatorState


class ElevatorSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    state = serializers.CharField(required=False)
    total_number_of_floors = serializers.IntegerField(required=True, min_value=1)
    floors_not_in_use = serializers.JSONField(required=False)
    capacity_in_person = serializers.IntegerField(required=True, min_value=1)
    current_floor = serializers.IntegerField(required=True, min_value=0)

    class Meta:
        model = Elevator
        fields = '__all__'

    def validate(self, attrs) -> dict:
        validated_data = super().validate(attrs)
        if validated_data.get("floors_not_in_use"):
            # Only list of integers are allowed
            if not isinstance(validated_data.get("floors_not_in_use"), list) or \
                    not all(isinstance(floor, int) for floor in validated_data.get("floors_not_in_use")):
                raise serializers.ValidationError("Floors not in use must be a list of integers")
            # This is required to avoid having duplicate values
            validated_data["floors_not_in_use"] = list(set(validated_data.get("floors_not_in_use")))
            # All floors in floors_not_in_use must be less than total_number_of_floors
            if validated_data.get('total_number_of_floors') and max(validated_data.get("floors_not_in_use")) > \
                    validated_data.get('total_number_of_floors'):
                raise serializers.ValidationError("Floors not in use must be less than Total number of floors")
            # current_floor must not be in floors_not_in_use
            if validated_data.get("current_floor") in validated_data.get("floors_not_in_use"):
                raise serializers.ValidationError("Current floor must not be in floors not in use")
        if validated_data.get('state'):
            try:
                validated_data['state'] = ElevatorState[validated_data.get('state').upper()]
            except KeyError:
                raise serializers.ValidationError("Invalid state")
        return validated_data

    def to_representation(self, instance) -> dict:
        data = super(ElevatorSerializer, self).to_representation(instance)
        data["state"] = instance.state.name
        return data
