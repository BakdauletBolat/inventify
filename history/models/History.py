from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from base.models import BaseModel
from django.db import models
import json


class History(BaseModel):
    action = models.CharField(max_length=255)
    instance = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('instance', 'object_id')
    edits = models.JSONField(default=dict)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["instance", "object_id"]),
        ]
