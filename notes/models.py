from django.db import models
from django.utils import timezone

class NoteCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    color = models.CharField(max_length=7, default='#3B82F6')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Note Categories'

class Note(models.Model):
    title = models.CharField(max_length=300)
    body = models.TextField(help_text="Supports Markdown")
    category = models.ForeignKey(NoteCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='notes')
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags e.g. #Emergency, #PaintCodes")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-updated_at']
