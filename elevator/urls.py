from django.urls import re_path, include
from rest_framework import routers

from elevator.views import ElevatorViewSet

router = routers.DefaultRouter()


router.register(r'elevator', ElevatorViewSet)

urlpatterns = [re_path(r"^", include(router.urls))]
