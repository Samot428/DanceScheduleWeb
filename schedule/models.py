from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from TrainerClubs.models import Club
# Create your models here.
User = get_user_model()

class UploadedScheduleFile(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='UploadedScheduleFile', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'UploadedScheduleFile')
    filename = models.CharField(max_length=225)
    file = models.FileField(upload_to = 'schedule_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    #  Optionally, you can link the file to a user
    # user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return self.filename
