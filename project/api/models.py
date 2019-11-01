from django.contrib.postgres.fields import ArrayField, JSONField
from django.db import models
import uuid


class Analyze(models.Model):
	img_data = models.FileField(max_length=None, null=True, blank=True)
	img_cube = JSONField(null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	def __str__(self):
		return self.text.img_data

class Note(models.Model):
	# img_uuid = models.CharField(max_length=255, null=True, blank=True)
	img_uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	img_data = models.FileField(max_length=None, null=True, blank=True)
	img_cube = JSONField(null=True, blank=True)
	img_standard = JSONField(blank=True, null=True)
	img_binary = models.BinaryField(blank=True, null=True)
	proccess = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	def __str__(self):
		return '{"img_uuid":"%s", "img_data":"%s", "proccess":%s}' % (self.img_uuid, self.img_data, self.proccess)



