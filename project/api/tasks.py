from project.api.serializers import *
from .models import *

from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route, action

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.core.files import File
from django.core.files.storage import FileSystemStorage

import os
import json
import datetime
import itertools
import numpy as np
import urllib
import psycopg2
from PIL import Image
import uuid

import face_recognition
from celery.decorators import task

def delete_analyzed(uuid):
	notes = Note.objects.all()
	note = get_object_or_404(notes, img_uuid=uuid)
	note.delete()

@task(name="tasks.delete_one_entity")
def delete_one_entity(uuid):
	notes = Note.objects.all()
	note = get_object_or_404(notes, img_uuid=uuid)
	note.delete()
	return "Entry deleted."

@task(name="tasks.get_one_entity")
def get_one_entity(uuid):
	print("get--------------------------")
	notes = Note.objects.all()
	note = get_object_or_404(notes, img_uuid=uuid)
	serializer = NoteSerializer(note,many=False)
	return serializer.data["img_uuid"]

@task(name="tasks.post_analyze")
def post_analyze(json_encoded):
	cur_cube_list = []
	cur_uuid_list = []
	cur_array_list = []

	notes = Note.objects.all()
	serializer = NoteSerializer(notes,many=True)
	query_list = serializer.data
	""" compare with faces in db """
	for i in range(len(query_list)):
		cur_cube = query_list[i]["img_cube"]
		cur_uuid = query_list[i]["img_uuid"]
		cur_uuid_list.append(cur_uuid)
		""" convert json back to numpy array """
		numpy_array = np.array(cur_cube)
		cur_cube_list.append(numpy_array)
	analyze_json = json.loads(json_encoded)
	analyze_numpy = np.array(analyze_json)
	results = face_recognition.compare_faces(cur_cube_list, analyze_numpy)
	
	found_uuid = "Unknown"
	if True in results:
		first_match_index = results.index(True)
		found_uuid = cur_uuid_list[first_match_index]
		delete_analyzed(found_uuid)
		found_uuid = found_uuid.strip('\"')
		return found_uuid
	return found_uuid


@task(name="tasks.post_entry")
def post_entry(json_encoded):
	""" face in image """
	js = '{"img_cube":%s, "proccess":"%s"}' % (json_encoded, True)
	post_req = json.loads(js, strict=False)
	""" post to database """
	serializer = NoteSerializer(data=post_req)
	serializer.is_valid(raise_exception=True)
	serializer.save()
	img_uuid = serializer.data["img_uuid"]
	img_uuid = img_uuid.strip('\"')
	return img_uuid

@task(name="tasks.get_entities")
def get_entities():
	notes = Note.objects.all()
	serializer = NoteSerializer(notes, context={'request': None}, many=True)
	return serializer.data


