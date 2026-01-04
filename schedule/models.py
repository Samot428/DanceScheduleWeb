from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class UploadedScheduleFile(models.Model):
    filename = models.CharField(max_length=225)
    file = models.FileField(upload_to = 'schedule_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    #  Optionally, you can link the file to a user
    # user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return self.filename
