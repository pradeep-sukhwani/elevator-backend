from django.db import models
from enum import Enum, auto
from enumchoicefield import EnumChoiceField


class ElevatorState(Enum):
    IDLE = auto()
    MOVING = auto()
    DOOR_OPEN = auto()
    DOOR_CLOSE = auto()
    USER_STOP = auto()
    UNDER_MAINTENANCE = auto()


class Elevator(models.Model):
    name = models.CharField(max_length=30, help_text="Name of the elevator")
    state = EnumChoiceField(ElevatorState, default=ElevatorState.IDLE,
                            help_text="Shows the current state of Elevator")
    total_number_of_floors = models.IntegerField(default=1, help_text="Number of floors in the building")
    floors_not_in_use = models.JSONField(null=True, blank=True,
                                         help_text="Floors that are not in use. Elevator will not stop on these floors")
    capacity_in_person = models.IntegerField(default=1, help_text="Maximum number of people allowed in the elevator")
    current_floor = models.IntegerField(help_text="Show the current floor")

    def __str__(self):
        return self.name


class ElevatorRequest(models.Model):
    elevator = models.ForeignKey(Elevator, on_delete=models.PROTECT, related_name='elevatorrequest')
    pick_from_floor_number = models.IntegerField(help_text="Floor number where the elevator is called", default=0)
    drop_at_floor_number = models.IntegerField(help_text="Floor number passenger wants to go to", default=0)
    number_of_passengers = models.IntegerField(help_text="Number of passengers that are waiting for the elevator",
                                               default=0)
    is_completed = models.BooleanField(default=False, help_text="Shows if the request is completed")
    created_date = models.DateTimeField(auto_now_add=True, help_text="Date and time when the request was created")

    def __str__(self):
        return f"{self.elevator.name} requests"

