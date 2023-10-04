from django.db.models import Q

from elevator.models import ElevatorRequest, ElevatorState, Elevator


def find_the_closest_elevator(pick_from_floor_number: int, total_number_of_passengers: int, drop_at_floor_number: int) -> Elevator | None:
    # Exclude elevators that are under maintenance or user stopped
    # pick_from_floor_number and drop_at_floor_number should not be in floors_not_in_use
    # total_number_of_floors should be less than or equal to pick_from_floor_number
    # total_number_of_passengers should be less than or equal to capacity_in_person
    # Todo for future case, assign multiple elevators if the number of passengers is more than the capacity of the elevator
    elevators_query_set = Elevator.objects.filter(~Q(state__in=[ElevatorState.UNDER_MAINTENANCE, ElevatorState.USER_STOP]),
                                                  ~Q(floors_not_in_use__contains=pick_from_floor_number),
                                                  ~Q(floors_not_in_use__contains=drop_at_floor_number),
                                                  total_number_of_floors__gte=pick_from_floor_number,
                                                  capacity_in_person__gte=total_number_of_passengers
                                                  )
    if not elevators_query_set:
        return None
    nearest_elevator_objects = {}
    if elevators_query_set.filter(current_floor=pick_from_floor_number):
        return elevators_query_set.get(current_floor=pick_from_floor_number)

    # If no elevator is available on the same floor, then find the elevator that is nearest to the floor
    for elevator_object in elevators_query_set:
        floor_difference = abs(elevator_object.current_floor - pick_from_floor_number)
        if nearest_elevator_objects.get(floor_difference):
            nearest_elevator_objects.get(floor_difference).append(elevator_object)
        else:
            nearest_elevator_objects.update({abs(elevator_object.current_floor - pick_from_floor_number): [elevator_object]})
    # Nearest elevator is the one that has the least floor difference
    least_floor_difference = min(nearest_elevator_objects.keys())
    list_of_nearest_elevators = nearest_elevator_objects.get(least_floor_difference)
    return list_of_nearest_elevators[0]


def process_elevator_request(elevator_request_object: ElevatorRequest) -> ElevatorRequest:
    elevator_object = elevator_request_object.elevator
    current_elevator_floor = elevator_object.current_floor
    called_elevator_floor = elevator_request_object.pick_from_floor_number
    drop_at_floor_number = elevator_request_object.drop_at_floor_number
    # Passengers waiting for the elevator
    # Assuming per floor 2 seconds are required for elevator to cross the floor
    # Assuming 1 second to open the door and 1 second to close the door
    # Assuming 1 second for passengers to get inside the elevator
    time_taken_to_process_request_in_seconds = abs(current_elevator_floor - called_elevator_floor) * 2 + 3
    elevator_object.state = ElevatorState.MOVING
    elevator_object.save(update_fields=['state'])
    # We can use time.sleep(1)
    for time_taken in range(time_taken_to_process_request_in_seconds):
        pass
    elevator_object.current_floor = called_elevator_floor
    elevator_object.state = ElevatorState.DOOR_OPEN
    elevator_object.save(update_fields=['current_floor', 'state'])
    elevator_object.state = ElevatorState.DOOR_CLOSE
    elevator_object.save(update_fields=['state'])

    # Passengers travelling to the destination
    # Assuming per floor 2 seconds are required for elevator to reach the floor
    # Assuming 1 second to open the door and 1 second to close the door
    # Assuming 1 second for passengers to get out of the elevator
    time_taken_to_process_request_in_seconds = abs(called_elevator_floor - drop_at_floor_number) * 2 + 3
    # We can use time.sleep(1)
    for time_taken in range(time_taken_to_process_request_in_seconds):
        pass
    elevator_object.current_floor = drop_at_floor_number
    elevator_object.state = ElevatorState.DOOR_OPEN
    elevator_object.save(update_fields=['current_floor', 'state'])
    # Passengers getting out of the elevator
    elevator_object.state = ElevatorState.DOOR_CLOSE
    elevator_object.save(update_fields=['state'])
    elevator_request_object.is_completed = True
    elevator_request_object.save(update_fields=['is_completed'])
    return elevator_request_object
