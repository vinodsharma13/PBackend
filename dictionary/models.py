from django.db import models
from django.contrib.auth.models import User  # ✅ Import User model

class Word(models.Model):  # ✅ Renamed from Paribhasha to Word
    hindi = models.CharField(max_length=100, unique=True)
    hinglish = models.CharField(max_length=100)
    pageno = models.IntegerField(null=True, blank=True)

    # ✅ New Fields
    reviewed = models.BooleanField(default=False)  # Checkbox for review status
    review_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)  # Stores reviewer


    class Meta:
        verbose_name = "Word"
        verbose_name_plural = "Words"

    def __str__(self):
        return self.hindi


class Paribhasha(models.Model):  # ✅ Renamed from ParibhashaLine to Paribhasha
    word = models.ForeignKey(Word, related_name="paribhashas", on_delete=models.CASCADE, null=True)
    description = models.TextField(max_length=600)

    class Meta:
        verbose_name = "Paribhasha"
        verbose_name_plural = "Paribhashas"

    def __str__(self):
        return self.description[:50]  # Show first 50 chars
