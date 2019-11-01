from rest_framework import serializers
from project.api.models import *

from django.core.files.base import ContentFile
import base64
import uuid
import imghdr


class AnalyzeSerializer(serializers.ModelSerializer):
	class Meta:
		model = Analyze
		fields = ('id', 'img_data', 'img_cube')

class UploadSerializer(serializers.ModelSerializer):
	class Meta:
		model = Note
		fields = ('img_data',)
		# fields = ('img_uuid', 'img_data')

class NoteSerializer(serializers.ModelSerializer):
	class Meta:
		model = Note
		fields = ('img_uuid', 'img_data','img_cube','img_standard','img_binary','proccess')
		lookup_field = 'img_uuid'
		extra_kwargs = {
			'url': {'lookup_field': 'img_uuid'},
		}