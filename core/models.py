from django.db import models

class TestRun(models.Model):
    objects = None
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    log_path = models.TextField()
    report_path = models.TextField()
