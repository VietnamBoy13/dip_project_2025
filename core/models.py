
from django.db import models

class TestRun(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20)
    log_path = models.TextField()
