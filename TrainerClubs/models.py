from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Club(models.Model):
    club_owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='clubs')
    name = models.CharField(max_length=100)
    profile_picture = models.ImageField(upload_to='club_profiles/', blank=True, null=True)

    def __str__(self):
        return self.name
