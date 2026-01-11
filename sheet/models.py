from django.db import models
from TrainerClubs.models import Club
class SheetCell(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='SheetCells', null=True, blank=True)
    row = models.IntegerField()
    col = models.CharField(max_length=50)
    value = models.TextField(blank=True)
    color = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"({self.row}, {self.col})"
