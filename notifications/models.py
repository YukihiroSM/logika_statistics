from django.db import models


class Notification(models.Model):
    title = models.CharField(max_length=256)
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    notification_username = models.CharField(max_length=256)
    notification_type = models.CharField(max_length=256)
    generated_by = models.CharField(max_length=256)
