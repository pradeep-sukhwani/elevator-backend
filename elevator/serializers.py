import json

from rest_framework import serializers
from elevator.models import Elevator, ElevatorState, ElevatorRequest
from elevator.utils import find_the_closest_elevator


class ElevatorRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElevatorRequest
        fields = '__all__'


class ElevatorSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    state = serializers.CharField(required=False)
    total_number_of_floors = serializers.IntegerField(required=True, min_value=1)
    floors_not_in_use = serializers.JSONField(required=False)
    capacity_in_person = serializers.IntegerField(required=True, min_value=1)
    current_floor = serializers.IntegerField(required=True, min_value=0)
    elevator_requests = ElevatorRequestSerializer(required=False, many=True, source='elevatorrequest')
    next_floor_details = serializers.SerializerMethodField()
    elevator_direction = serializers.SerializerMethodField()

    class Meta:
        model = Elevator
        fields = '__all__'

    def get_next_floor_details(self, obj):
        elevator_requests = obj.elevatorrequest.filter(is_completed=False)
        if elevator_requests.exists():
            elevator_request = elevator_requests.first()
            return {"next_floor": elevator_request.pick_from_floor_number,
                    "number_of_passengers": elevator_request.number_of_passengers,
                    "drop_at_floor_number": elevator_request.drop_at_floor_number}
        return None

    def get_elevator_direction(self, obj):
        elevator_requests = obj.elevatorrequest.filter(is_completed=False)
        if elevator_requests.exists():
            elevator_request = elevator_requests.first()
            if elevator_request.pick_from_floor_number > elevator_request.drop_at_floor_number:
                return "Going Up"
            else:
                return "Going Down"
        return None

    def validate(self, attrs) -> dict:
        validated_data = super().validate(attrs)
        if validated_data.get("floors_not_in_use"):
            # Only list of integers are allowed
            if not isinstance(validated_data.get("floors_not_in_use"), list) or \
                    not all(isinstance(floor, int) for floor in validated_data.get("floors_not_in_use")):
                raise serializers.ValidationError({"floors_not_in_use": "Floors not in use must be a list of integers"})
            # This is required to avoid having duplicate values
            validated_data["floors_not_in_use"] = list(set(validated_data.get("floors_not_in_use")))
            # All floors in floors_not_in_use must be less than total_number_of_floors
            if validated_data.get('total_number_of_floors') and max(validated_data.get("floors_not_in_use")) > \
                    validated_data.get('total_number_of_floors'):
                raise serializers.ValidationError({"floors_not_in_use": "Floors not in use must be less than Total number of floors"})
            # current_floor must not be in floors_not_in_use
            if validated_data.get("current_floor") in validated_data.get("floors_not_in_use"):
                raise serializers.ValidationError({"floors_not_in_use": "Current floor must not be in floors not in use"})
        if validated_data.get('state'):
            try:
                validated_data['state'] = ElevatorState[validated_data.get('state').upper()]
            except KeyError:
                raise serializers.ValidationError({"state": "Invalid state"})
        return validated_data

    def to_representation(self, instance) -> dict:
        data = super(ElevatorSerializer, self).to_representation(instance)
        data["state"] = instance.state.name
        return data


class CreateElevatorRequestSerializer(serializers.ModelSerializer):
    pick_from_floor_number = serializers.IntegerField(required=True, min_value=0)
    drop_at_floor_number = serializers.IntegerField(required=True, min_value=0)
    number_of_passengers = serializers.IntegerField(required=True, min_value=1)
    stop_elevator = serializers.BooleanField(default=False)

    class Meta:
        model = ElevatorRequest
        fields = ['pick_from_floor_number', 'drop_at_floor_number', 'number_of_passengers', 'stop_elevator']

    def validate(self, attrs) -> dict:
        validated_data = super().validate(attrs)
        if validated_data.get("pick_from_floor_number") == validated_data.get("drop_at_floor_number"):
            raise serializers.ValidationError({"drop_at_floor_number": "Drop at floor number must be different from pick from floor number"})
        elevator_object: Elevator | None = find_the_closest_elevator(pick_from_floor_number=validated_data.get("pick_from_floor_number"),
                                                                     total_number_of_passengers=validated_data.get("number_of_passengers"),
                                                                     drop_at_floor_number=validated_data.get('drop_at_floor_number'))
        validated_data['elevator'] = elevator_object
        if not elevator_object:
            raise serializers.ValidationError({"elevator": "Elevator is not available at the moment for the requested floor"})
        return validated_data

    def create(self, validated_data) -> ElevatorRequest:
        elevator_object = validated_data.get('elevator')
        stop_elevator = validated_data.pop('stop_elevator', None)
        if stop_elevator:
            # Update the state of elevator to USER_STOP
            elevator_object.state = ElevatorState.USER_STOP
            elevator_object.save(update_fields=['state'])
        else_object = super(CreateElevatorRequestSerializer, self).create(validated_data)
        return else_object
