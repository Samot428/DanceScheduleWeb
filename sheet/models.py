from django.db import models

class SheetCell(models.Model):
    row = models.IntegerField()
    col = models.CharField(max_length=50)
    value = models.TextField(blank=True)
    color = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"({self.row}, {self.col})"
