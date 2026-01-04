
from django.db import models
import json
from datetime import time

# Create your models here.
class Dancer(models.Model):
    name = models.CharField(max_length=200)
    time_availability = models.CharField(max_length=1000)

    def __str__(self):
        return self.name
    
    def get_time(self):
        """Return time_availability as a dictionary"""
        try:
            return json.loads(self.time_availability) if self.time_availability else {}
        except (json.JSONDecodeError, TypeError):
            return {}

class Couple(models.Model):
    name = models.CharField(max_length=200)
    min_duration = models.IntegerField(default=60)
    group = models.ForeignKey('Group', on_delete=models.CASCADE, related_name='couples', null=True, blank=True)
    dance_class_lat = models.CharField(max_length=100,)
    dance_class_stt = models.CharField(max_length=100,)
    def __str__(self):
        return self.name

    def nlt(self):
        return self.name, self.dance_class_stt, self.dance_class_lat

    def dancers_names(self):
        """Parse the couple name to extract individual dancer names"""
        name = str(self.name)
        if " and " in name:
            fd, sd = name.split(" and ")
            fd = fd.rstrip()
            sd = sd.rstrip()
            return fd, sd
        elif " a " in name:
            fd, sd = name.split(" a ")
            fd = fd.rstrip()
            sd = sd.rstrip()
            return fd, sd
        return None, None
    
    def extract_times(self, ft, st):
        """Extract common time windows for both dancers"""
        f_keys = ft.keys() if isinstance(ft, dict) else []
        s_keys = st.keys() if isinstance(st, dict) else []
        times = []
        for t in f_keys:
            if t in s_keys:
                times.append(t)
        return times
    
    def time_avail(self):
        """Calculate availability for the pair based on both dancers"""
        # Get dancer names
        fd_name, sd_name = self.dancers_names()
        if not fd_name or not sd_name:
            return {}
        
        # Find dancer objects
        try:
            fd = Dancer.objects.get(name=fd_name.strip())
            sd = Dancer.objects.get(name=sd_name.strip())
        except Dancer.DoesNotExist:
            return {}
        
        # Get times for both dancers (now returns dict)
        ft = fd.get_time()
        st = sd.get_time()
        
        # Extract common times
        times = self.extract_times(ft, st)
        
        time_availability = {}
        for t in times:
            # Both dancers must be available (check boolean values)
            time_availability[t] = ft.get(t) and st.get(t)
        
        return time_availability
    
    def get_time(self):
        """Get the availability for this couple"""
        return self.time_avail()

class Trainer(models.Model):
    name = models.CharField(max_length = 200)
    group_lesson = models.ManyToManyField('GroupLesson', related_name='trainer', blank=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    focus = models.CharField(max_length=10, default="S&L")

    def __str__(self):
        return self.name
    def get_availability(self):
        return self.start_time, self.end_time
    def group_lesson_time(self):
        return self.group_lesson

class Day(models.Model):
    name = models.CharField(max_length=200)
    couples = models.ManyToManyField('Couple', related_name='days', blank=True)
    start_time = models.TimeField(default=time(8,0))
    end_time = models.TimeField(default=time(21,0))
    trainers = models.ManyToManyField('Trainer', related_name='day', blank=True)
    def __str__(self):
        return self.name
    def add_trainer(self, trainer):
        trainer = Trainer.objects.get(name=trainer) 
        self.trainers[trainer.__str__()] = trainer.group_lesson_time()
        return f"{trainer} added"
    def remove_trainer(self, trainer):
        trainer = Trainer.objects.get(name=trainer)
        del self.trainers[trainer.__str__()]
        return f"{trainer} removed"
    
class Group(models.Model):
    name = models.CharField(max_length=200)
    index = models.IntegerField(default=0)  # For sorting groups
    couples = []
    def __str__(self):
        return self.name

    def get_couples(self):
        return self.couples
    def add_couple(self, couple):
        self.couples.append(Couple.objects.get(name=couple))
        return f"{couple} added"
    def remove_couple(self, couple):
        self.couples.remove(Couple.objects.get(name=couple))
        return f"{couple} removed"

class GroupLesson(models.Model):
    day = models.ForeignKey('Day', on_delete=models.CASCADE, related_name='group_lessons', null=True, blank=True)
    groups = models.ManyToManyField('Group', related_name='group_lessons', blank=True)
    time_interval_start = models.TimeField(default=time(0, 0))
    time_interval_end = models.TimeField(default=time(0, 0))

    def __str__(self):
        return f"{self.time_interval_start}-{self.time_interval_end}"

class TrainerDayAvailability(models.Model):
    """Per-day availability for a trainer, avoiding global overwrites."""
    day = models.ForeignKey('Day', on_delete=models.CASCADE, related_name='trainer_availabilities')
    trainer = models.ForeignKey('Trainer', on_delete=models.CASCADE, related_name='day_availabilities')
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        unique_together = ('day', 'trainer')

    def __str__(self):
        return f"{self.trainer.name} @ {self.day.name}: {self.start_time}-{self.end_time}"

class DancersAvailability(models.Model):
    dancer = models.ForeignKey('Dancer', on_delete=models.CASCADE, related_name='dancer_availabilities')
    day = models.ForeignKey('Day', on_delete=models.CASCADE, related_name='dancer_availabilities')
    availability = models.JSONField(default=list)  # Stores [True, False, True, ...]
    
    def __str__(self):
        return f"{self.dancer.name} @ {self.day.name}: {self.availability}"
