from django import template
from ..models import TrainerDayAvailability

register = template.Library()

@register.filter
def trainer_start_for_day(day, trainer):
    try:
        availability = TrainerDayAvailability.objects.get(day=day, trainer=trainer)
        return availability.start_time
    except TrainerDayAvailability.DoesNotExist:
        return day.start_time

@register.filter
def trainer_end_for_day(day, trainer):
    try:
        availability = TrainerDayAvailability.objects.get(day=day, trainer=trainer)
        return availability.end_time
    except TrainerDayAvailability.DoesNotExist:
        return day.end_time
