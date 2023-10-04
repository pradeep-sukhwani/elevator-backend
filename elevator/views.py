from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from elevator.models import Elevator, ElevatorState, ElevatorRequest
from elevator.serializers import ElevatorSerializer, CreateElevatorRequestSerializer, ElevatorRequestSerializer
from elevator.utils import process_elevator_request


class ElevatorViewSet(viewsets.ModelViewSet):
    """
    Elevator API for getting and updating elevators.
    To create/update an elevator, we can use the following format:
        `name`: <str>: "Elevator 1"
        `total_number_of_floors`: <int>: 10
        `floors_not_in_use`: <list>: [1, 2, 3]
        `capacity_in_person`: <int>: 10
        `current_floor`: <int>: 1
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
            - requests
                - completed: for completed request
                - not_completed: for pending requests
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
        if query_params.get("requests"):
            requests = query_params.get("requests")
            if requests == "completed":
                return self.queryset.filter(elevatorrequest__is_completed=True).distinct()
            elif requests == "not_completed":
                return self.queryset.filter(elevatorrequest__is_completed=False).distinct()
            else:
                return self.queryset.none()
        return self.queryset.all()


class ElevatorRequestViewSet(viewsets.ModelViewSet):
    """
    ElevatorRequest API for creating elevators requests.
    To create an elevator request, we can use the following format:
    `pick_from_floor_number`: <int>: 1 (Floor number where the elevator is called)
    `drop_at_floor_number`: <int>: 2 (Floor number where the elevator needs to go)
    `number_of_passengers`: <int>: 3 (Number of persons that are waiting for the elevator)
    `stop_elevator`: <bool>: True/False
        if stop_elevator is True, then the elevator will stop at the current floor and won't proceed ahead. However,
        it is still saves the request.
    """
    queryset = ElevatorRequest.objects.all()
    serializer_class = CreateElevatorRequestSerializer

    def get_serializer_class(self):
        """
        This method is used to get the serializer class based on the request method.
        """
        if self.action in ["process_elevator_requests"] or self.request.method == 'GET':
            return ElevatorRequestSerializer
        return super(ElevatorRequestViewSet, self).get_serializer_class()

    @action(detail=True, methods=["post"])
    def process_elevator_requests(self, request, *args, **kwargs):
        """
        This view is used to process the elevator requests.
        """
        # Todo: Convert this into an asynchronous task
        elevator_request_object = self.get_object()
        if elevator_request_object.is_completed:
            return Response({"error": "Elevator request is completed"}, status=status.HTTP_400_BAD_REQUEST)
        process_elevator_request(elevator_request_object)
        elevator_request_object.refresh_from_db()
        serializer = self.get_serializer(elevator_request_object)
        return Response(serializer.data, status=status.HTTP_200_OK)
