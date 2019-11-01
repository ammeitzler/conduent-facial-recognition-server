from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import face_recognition
from scipy.spatial import Delaunay
import random
import numpy
from numpy import linalg as LA
import struct
import math
import sys

def rnd(x, y):
	m = math.fmod(x, y)
	if m < y/2.0:
		return x-m	
	else:
		return x+(y-m)

def process_file(input_file, output_file):
	
	max_points = 1000
	merge_percent = 500
	save_debug_images = False
	
	image = face_recognition.load_image_file(input_file)

	face_landmarks_list_ = face_recognition.face_landmarks(image)
	face_landmarks_list = [face_landmarks_list_[0]]
	face_locations = face_recognition.face_locations(image)


	im = Image.open(input_file)
	pil_image = Image.new('RGB', im.size, color = 'black')
	d = ImageDraw.Draw(pil_image)


	input_points = []

	feature_min = 99999
	feature_max = 0

	eye_centers = []
	mouth = (0,0)
	for face_landmarks in face_landmarks_list:
		for facial_feature in face_landmarks.keys():
			d.line(face_landmarks[facial_feature], width=2)
			if facial_feature is "left_eye" or facial_feature is "right_eye":
				avg = (0,0)
				l = 0
				for pt in face_landmarks[facial_feature]:
					avg = (avg[0] + pt[0], avg[1] + pt[1])
					l = l + 1
				avg = (avg[0]/l, avg[1]/l)
				eye_centers.append(avg)
			if facial_feature is not "nose_bridge":
				for pt in face_landmarks[facial_feature]:
					if pt[0] < feature_min:
						feature_min = pt[0]
					if pt[0] > feature_max:
						feature_max = pt[0]
					input_points.append(pt)

	feature_width = abs(feature_max-feature_min)

	feature_min = feature_min - feature_width/20
	feature_max = feature_max + feature_width/20

	edge_image = im.copy()
	edge_image = edge_image.filter(ImageFilter.FIND_EDGES)

	enhancer = ImageEnhance.Contrast(edge_image) 
	edge_image = enhancer.enhance(2)

	#edge_image = edge_image.filter(ImageFilter.EDGE_ENHANCE)
	#edge_image = edge_image.filter(ImageFilter.EDGE_ENHANCE_MORE)

	#max_points = 30
	points_placed = 0

	edge_points = []
	border = 20

	feature_distance = 60

	for loc in face_locations:
		aloc = (loc[0] - (loc[2]-loc[0])/2, loc[1] + (loc[1]-loc[3])/2, loc[2], loc[3] - (loc[1]-loc[3])/2)
		#if x > aloc[3] and x < aloc[1] and y > aloc[0] and y < aloc[2]:
		for y in range(int(aloc[0]), int(aloc[2])):
			for x in range(int(aloc[3]), int(aloc[1])):
				if x > feature_min and x < feature_max:
					px = edge_image.getpixel((x, y))
					brightness = (im.getpixel((x,y))[0] + im.getpixel((x,y))[1] + im.getpixel((x,y))[2]) / 3
					probability = brightness
					max_brightness = 200
					eye_distance = 9999
					edge_min = 100
					for eye in eye_centers:
						distance = math.sqrt(math.pow(eye[0]-x, 2) + math.pow(eye[1]-y, 2))
						if distance < eye_distance:
							eye_distance = distance
					if eye_distance < 10:
						probability = 0
						max_brightness = 200
						edge_min = 80
					random_insert = random.randint(0, 1000) > 997
					if random_insert or (brightness < max_brightness and random.randint(0, 600) > probability and px[2] > edge_min):
						edge_points.append((x,y))
					

	de = ImageDraw.Draw(edge_image)

	for ep in edge_points:
		#filter out points below the jawline
		doAppend = True
		for face_landmarks in face_landmarks_list:
			lastPt = None
			for pt in face_landmarks['chin']:
				de.rectangle([pt, (pt[0]+10, pt[1]+10)], fill=(0, 255, 255, 255))
			if lastPt is not None:
				vec = (pt[0] - lastPt[0], pt[1] - lastPt[1])
				vecNorm = LA.norm(vec)
				vec = (vec[1]/vecNorm, -vec[0]/vecNorm)
				de.line([lastPt, (lastPt[0] + vec[0], lastPt[1] + vec[1])], fill=(255, 0, 0, 255), width=3)
				vecToPt = (ep[0] - lastPt[0], ep[1] - lastPt[1])
				vecNorm = LA.norm(vecToPt)
				if vecNorm == 0:
					vecNorm = 0000.1
				vecToPt = (vecToPt[0]/vecNorm, vecToPt[1]/vecNorm)
				if numpy.dot(vec, vecToPt) < -0.5:
					de.line([lastPt, (lastPt[0] + vecToPt[0] * 2000, lastPt[1] + vecToPt[1] * 2000)], fill=(255, 255, 0, 255), width=2)
					doAppend = False
			lastPt = (pt[0], pt[1])
		for face_landmarks in face_landmarks_list:
			for pt in face_landmarks['nose_tip']:
				if ep[1] < pt[1]:
					doAppend = True

		if doAppend:
			input_points.append(ep)
			de.rectangle([ep, (ep[0]+10, ep[1]+10)], fill=(0, 255, 0, 255))
		else:
			de.rectangle([ep, (ep[0]+10, ep[1]+10)], fill=(255, 0, 0, 255))

	if save_debug_images:
		for loc in face_locations:
			face_location = (loc[0] - (loc[2]-loc[0])/2, loc[1] + (loc[1]-loc[3])/2, loc[2], loc[3] - (loc[1]-loc[3])/2)
			top, right, bottom, left = face_location
			de.rectangle([left, top, right, bottom], outline=(255, 255, 0, 255))
			face_image = image[top:bottom, left:right]
			fimage = Image.fromarray(face_image)
			fimage.save('face.png')

	if save_debug_images:
		edge_image.save('edges.png')

	pmin = [edge_image.size[0], edge_image.size[1]]
	pmax = [0, 0]

	#merge vertices

	merged_points = []
	merge_thresh = 3
	for i in input_points:
		merge = False
		for m in merged_points:
			if abs(i[0] - m[0]) < merge_thresh and abs(i[1] - m[1]) < merge_thresh:
				merge = True
		if not merge:
			merged_points.append(i)

	for p in merged_points:
		if p[0] > pmax[0]:
			pmax[0] = p[0]
		if p[1] > pmax[1]:
			pmax[1] = p[1]
		if p[0] < pmin[0]:
			pmin[0] = p[0]
		if p[1] < pmin[1]:
			pmin[1] = p[1]

	tri = Delaunay(merged_points)

	tri_normalized = []
	tri_normalized_thick = []

	psize = pmax[0] - pmin[0]
	if pmax[1] - pmin[1] > psize:
		psize = pmax[1] - pmin[1]
	psize = float(psize)

	tri_colors = []
	norm_min = 99999.0
	norm_max = 0.0
	for t in tri.simplices:
	  #  print("Line: {}".format(t))
		triline = [merged_points[t[0]], merged_points[t[1]], merged_points[t[2]], merged_points[t[0]]]
		pn0 = [float(triline[0][0]-pmin[0])/psize, float(triline[0][1]-pmin[1])/psize]
		pn1 = [float(triline[1][0]-pmin[0])/psize, float(triline[1][1]-pmin[1])/psize]
		pn2 = [float(triline[2][0]-pmin[0])/psize, float(triline[2][1]-pmin[1])/psize]

		px = int((triline[0][0] + triline[1][0] + triline[2][0])/3)
		py = int((triline[0][1] + triline[1][1] + triline[2][1])/3)
		color = im.getpixel((px, py))

		eye_distance = 9999
		edge_min = 100
		for eye in eye_centers:
			distance = math.sqrt(math.pow(eye[0]-px, 2) + math.pow(eye[1]-py, 2))
			if distance < eye_distance:
				eye_distance = distance
		if eye_distance < 5:
			color = (color[0]/1.5, color[1]/1.5, color[2]/1.5)
		else:
			color = (min(255, color[0]*2), min(255, color[1]*2), min(255, color[2]*2))	

		color =  (min(255, color[0]+20), min(255, color[1]+20), min(255, color[2]+20))
		tri_colors.append(color)
		
		if pn0[0] < norm_min:
			norm_min = pn0[0]
		if pn1[0] < norm_min:
			norm_min = pn1[0]
		if pn2[0] < norm_min:
			norm_min = pn2[0]

		if pn0[0] > norm_max:
			norm_max = pn0[0]
		if pn1[0] > norm_max:
			norm_max = pn1[0]
		if pn2[0] > norm_max:
			norm_max = pn2[0]

		tri_normalized.append([pn0, pn1, pn2])
		#if random.randint(0, 10) > 3:
		d.line(triline, width=2)

	#recenter
	x_offset = -(norm_min + abs(norm_max-norm_min)/2.0)

	#tri_centered = []
	#for tri in tri_normalized:
	#	tri_centered.append([(tri[0][0] + x_offset, tri[0][1]), (tri[1][0] + x_offset, tri[1][1]), (tri[2][0] + x_offset, tri[2][1])])
	#tri_normalized = tri_centered

	#fill thick array
	for face_landmarks in face_landmarks_list:
		for facial_feature in face_landmarks.keys():
			if facial_feature is "chin":
				thick_line = []
				for pt in face_landmarks[facial_feature]:
					pn0 = (float(pt[0]-pmin[0])/psize, float(pt[1]-pmin[1])/psize)
					thick_line.append(pn0)
				tri_normalized_thick.append(thick_line)

	for face_landmarks in face_landmarks_list:
		for facial_feature in face_landmarks.keys():
			d.line(face_landmarks[facial_feature], width=5)
	
	if save_debug_images:
		pil_image.save("out.png")

	#snap to grid
#	tri_snapped = []
#	gridsize = 1.0/32.0
#	for t in tri_normalized:
#		triline = []
#		for pt in t:
#			triline.append((rnd(pt[0], gridsize), rnd(pt[1], gridsize)))
#		tri_snapped.append(triline)
#	tri_normalized = tri_snapped
#
#	thick_snapped = []
#	for line in tri_normalized_thick:
#		sline = []
#		for pt in line:
#			sline.append((rnd(pt[0], gridsize), rnd(pt[1], gridsize)))
#		thick_snapped.append(sline)
#	tri_normalized_thick = thick_snapped

	bigsize = 1024
	big_image = Image.new('RGB', (bigsize, bigsize), color = 'white')
	db = ImageDraw.Draw(big_image)

	draw_filled = False
	draw_both = False

	if draw_both:
		bigsize = float(bigsize)
		idx = 0
		for t in tri_normalized:
			triline = [(t[0][0] * bigsize, t[0][1] * bigsize), (t[1][0] * bigsize, t[1][1] * bigsize), (t[2][0] * bigsize, t[2][1] * bigsize)]
			color = tri_colors[idx]
			val = (color[0] + color[1] + color[2]) / 3
			val = float(val) / 255.0
			val = val * val * 3.0
			val = int(val * 255.0)
			db.polygon(triline, fill=(val, val, val, 255))
			idx = idx + 1
		for t in tri_normalized:
			triline = [(t[0][0] * bigsize, t[0][1] * bigsize), (t[1][0] * bigsize, t[1][1] * bigsize), (t[2][0] * bigsize, t[2][1] * bigsize)]
			db.line(triline, width=2, fill=(0, 0, 0, 255))
		for line in tri_normalized_thick:
			bigline = []
			for pt in line:
				bpt = (pt[0] * bigsize, pt[1] * bigsize)
				bigline.append(bpt)
			db.line(bigline, width = 2, fill=(0, 0, 0, 255))

	elif draw_filled:
		bigsize = float(bigsize)
		idx = 0
		for t in tri_normalized:
			triline = [(t[0][0] * bigsize, t[0][1] * bigsize), (t[1][0] * bigsize, t[1][1] * bigsize), (t[2][0] * bigsize, t[2][1] * bigsize)]
			db.polygon(triline, fill=tri_colors[idx])
			idx = idx+1
	else:
		bigsize = float(bigsize)
		for t in tri_normalized:
			triline = [(t[0][0] * bigsize, t[0][1] * bigsize), (t[1][0] * bigsize, t[1][1] * bigsize), (t[2][0] * bigsize, t[2][1] * bigsize)]
			db.line(triline, width=2, fill=(0, 0, 0, 255))

	big_lines = []
	for line in tri_normalized_thick:
		bigline = []
		for pt in line:
			bpt = (pt[0] * bigsize, pt[1] * bigsize)
			bigline.append(bpt)
		db.line(bigline, width = 4, fill=(0, 0, 0, 255))
	
	if save_debug_images:
		big_image.save('big.png')

	output_file = "project/media/" + output_file
	fout = open(output_file, 'wb')
	fout.write(struct.pack('i', len(tri_normalized)))

	idx = 0
	for t in tri_normalized:
		fout.write(struct.pack('ffffff', t[0][0]+x_offset, t[0][1], t[1][0]+x_offset, t[1][1], t[2][0]+x_offset, t[2][1]))
		color = tri_colors[idx]
		fout.write(struct.pack('fff', color[0]/255.0, color[1]/255.0, color[2]/255.0))
		idx = idx + 1

	fout.close()

if len(sys.argv) < 3:
	print("Syntax: stylize.py source_image.(png|jpg) output.bin")
else:
	print(sys.argv[1])
	# process_file(sys.argv[1], sys.argv[2])


