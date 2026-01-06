from django.contrib import admin
from .models import Dancer, Couple, Trainer, Group, Day, TrainerDayAvailability, GroupLesson
from TrainerClubs.models import Club
# Register your models here.

admin.site.register(Dancer)
admin.site.register(Couple)
admin.site.register(Trainer)
admin.site.register(Group)
admin.site.register(Day)
admin.site.register(TrainerDayAvailability)
admin.site.register(GroupLesson)
admin.site.register(Club)