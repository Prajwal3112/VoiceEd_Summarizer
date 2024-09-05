from django.db import models
import os

class AudioRecord(models.Model):
    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=255)
    text_file_path = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    duration = models.FloatField(null=True, blank=True)
    transcription = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.file_name} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"

    def save(self, *args, **kwargs):
        if not self.file_name:
            self.file_name = f"audio_{self.created_at.strftime('%Y%m%d_%H%M%S')}.wav"
        super().save(*args, **kwargs)
# Create your models here.
