from django.db import models


class PublicGroup(models.Model):
    name=models.CharField(max_length=255)
    chat_id = models.CharField(max_length=255)

    def __str__(self):
        return self.name