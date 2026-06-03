from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from devices.views import DeviceViewSet, ScheduleViewSet
from energy.views import EnergyViewSet

router = DefaultRouter()
router.register(r'devices', DeviceViewSet, basename='device')
router.register(r'schedules', ScheduleViewSet, basename='schedule')
router.register(r'energy', EnergyViewSet, basename='energy')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
]
