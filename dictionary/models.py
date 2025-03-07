from django.db import models

class Paribhasha(models.Model):
    hindi = models.CharField(max_length=100, unique=True)
    hinglish = models.CharField(max_length=100)
    pageno = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name = "Paribhasha"
        verbose_name_plural = "Paribhasha"

    def __str__(self):
        return self.hindi


class ParibhashaLine(models.Model):
    paribhasha = models.ForeignKey(Paribhasha, related_name="paribhasha", on_delete=models.CASCADE, null=True)
    name = models.TextField(max_length=600)

    class Meta:
        verbose_name = "Paribhasha Line"
        verbose_name_plural = "Paribhasha Lines"

    def __str__(self):
        return self.name[:50]  # Show first 50 chars
