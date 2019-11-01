from project.api.serializers import *
from .models import *
from .stylize import *

from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route, action
from rest_framework.exceptions import NotFound

from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db import transaction
from django.http import HttpResponse
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Max
from django.core.files.storage import default_storage

import itertools  
import json
from PIL import Image
import os
import datetime
import tempfile

from project.api.tasks import get_entities, post_entry, post_analyze, get_one_entity, delete_one_entity
import face_recognition
from django.core.files.storage import FileSystemStorage
from urllib.parse import urlparse
import urllib.request



class AnalyzeViewSet(viewsets.ModelViewSet):
	"""Handles creating, reading and updating items."""
	queryset = Analyze.objects.all()
	serializer_class = AnalyzeSerializer

	def list(self, request):
		""" compare with note dataset """
		combo_queryset = list(itertools.chain(Analyze.objects.all(), Note.objects.all()))
		serializer = AnalyzeSerializer(combo_queryset,context={'request': request}, many=True)
		return Response(serializer.data)

	def create(self, request, *args, **kwargs):
		if not request.POST._mutable:
			request.POST._mutable = True
		file = request.data['img_data']
		unknown_image = face_recognition.load_image_file(file)
		encodings = face_recognition.face_encodings(unknown_image)
		if len(encodings) > 0:
			unknown_image_encoding = encodings[0]
			json_encoded = json.dumps(unknown_image_encoding.tolist())
			""" send task to celery """
			res = post_analyze.delay(json_encoded)
			task_res = res.get()
			""" return with uuid """
			return HttpResponse(task_res.strip('\"'))
		else: 
			return Response("No faces found in image.")
		
		""" compare with note dataset """
		# combo_queryset = list(itertools.chain(Analyze.objects.all(), Note.objects.all()))
		# note_queryset = Note.objects.all()
		# note_serializer = AnalyzeSerializer(note_queryset,context={'request': request}, many=True)
		# print(note_serializer)

class NoteViewSet(viewsets.ModelViewSet):
	"""Handles creating, reading and updating items."""
	queryset = Note.objects.all()
	serializer_class = NoteSerializer
	upload_serializer = UploadSerializer

	lookup_field = 'img_uuid'

	def get_serializer_class(self):
		if self.request.method == 'POST':
			return UploadSerializer
		return UploadSerializer

	def create(self, request, img_uuid=None):
		if not request.POST._mutable:
			request.POST._mutable = True
		file = request.data['img_data']
		known_image = face_recognition.load_image_file(file)
		encodings = face_recognition.face_encodings(known_image)

		if len(encodings) > 0:
			known_image_encoding = encodings[0]
			json_encoded = json.dumps(known_image_encoding.tolist())
			""" send post task to celery """
			res = post_entry.delay(json_encoded)
			task_res = res.get()
			""" save jpeg to volume """
			n = '%s.jpeg' % task_res
			output_file_img = "project/media/" + n
			uploaded_image = Image.open(file)
			default_storage.save(n, file)
			uploaded_image.save(output_file_img)
			""" send jpeg to ivans file """
			output_file = 'vect-%s.mesh' % task_res
			process_file(file, output_file)
			""" path to new file in volume """
			file = open("project/media/" + output_file)
			file2 = open("project/media/" + n)
		else:
			return Response("No face in image detected.")
		""" return with uuid and binary data """
		return HttpResponse(task_res.strip('\"'))

	def list(self, request):
		res = get_entities.delay()
		task_res = res.get()
		return Response(task_res)

	""" return image encoding entities/foo/ """
	@method_decorator(cache_page(60))
	def retrieve(self, request, img_uuid=None):
		res = get_one_entity.delay(img_uuid)
		task_res = res.get()
		domain = request.build_absolute_uri('/')[:-1]
		# file = open("/media/vect-"+img_uuid+".mesh")
		# return HttpResponse(str(file), content_type='application/octet-stream')
		with urllib.request.urlopen(domain+"/media/vect-"+img_uuid+".mesh") as url:
			s = url.read()
			return HttpResponse(s, content_type='application/octet-stream')

	def destroy(self, request, img_uuid=None):
		res = delete_one_entity.delay(img_uuid)
		task_res = res.get()
		return HttpResponse(task_res)
