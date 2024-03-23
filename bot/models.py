from django.db import models


class LastRead(models.Model):
    update_id = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        # Ensure there is only one instance of this model in the database
        if not self.pk and LastRead.objects.exists():
            # If an instance already exists, don't save this one
            return
        super().save(*args, **kwargs)

    def __str__(self):
        return self.update_id