from django.utils import timezone
from ..models import TimeOverride


def get_current_time():
    override = TimeOverride.objects.first()
    if override and override.simulated_time is not None:
        return timezone.localtime(override.simulated_time)
    return timezone.localtime()


def set_simulated_time(dt):
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt)
    obj, _ = TimeOverride.objects.get_or_create(pk=1)
    obj.simulated_time = dt
    obj.save()


def clear_simulated_time():
    TimeOverride.objects.filter(pk=1).delete()
