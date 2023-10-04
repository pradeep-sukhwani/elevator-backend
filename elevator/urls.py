from django.urls import re_path, include
from rest_framework import routers

from elevator.views import ElevatorViewSet, ElevatorRequestViewSet

router = routers.DefaultRouter()


router.register(r'elevator', ElevatorViewSet)
router.register(r'elevator-request', ElevatorRequestViewSet)

urlpatterns = [re_path(r"^", include(router.urls))]
