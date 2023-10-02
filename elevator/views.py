from rest_framework import viewsets
from elevator.models import Elevator, ElevatorState
from elevator.serializers import ElevatorSerializer


class ElevatorViewSet(viewsets.ModelViewSet):
    """
    Elevator API for getting and updating elevators.
    To create/update an elevator, we can use the following format:
        `name`: <str>: "Elevator 1"
        `total_number_of_floors`: <int>: 10
        `floors_not_in_use`: <list>: [1, 2, 3]
        `capacity_in_person`: <int>: 10
        `state`: <str>: "IDLE"
            state can be one of the following:
                - IDLE
                - MOVING
                - DOOR_OPEN
                - DOOR_CLOSED
                - USER_STOP
                - UNDER_MAINTENANCE
    """
    queryset = Elevator.objects.all()
    serializer_class = ElevatorSerializer
    lookup_url_kwarg = "id"  # This is used to get the id from the url and pass it to the get_object method.
    http_method_names = ["get", "post", "patch"]

    def get_queryset(self):
        """
        This View filters the queryset based on the query params.
        We can filter the queryset based on the following query params:
            - name
            - state
        """
        query_params = self.request.query_params
        if query_params.get("name"):
            return self.queryset.filter(name__icontains=query_params.get("name"))
        if query_params.get("state"):
            state = query_params.get("state").upper()
            if state in ElevatorState.__members__:
                state_object = ElevatorState[state]
                return self.queryset.filter(state=state_object)
            else:
                return self.queryset.none()
        return self.queryset
