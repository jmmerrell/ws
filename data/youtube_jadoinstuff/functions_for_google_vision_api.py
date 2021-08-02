import httplib2
import sys
from googleapiclient import discovery
from oauth2client import tools, file, client
import json
import os
import cv2
from base64 import b64encode
import numpy as np


# limited preview only (sorry!) 
# API_DISCOVERY_FILE = os.environ.get('GOOGLE_VISION_API')
API_DISCOVERY_FILE = 'youtube_api_key'


""" Google Authentication Utilities """

def get_vision_api():
	credentials = get_api_credentials('https://www.googleapis.com/auth/cloud-platform')
	with open(API_DISCOVERY_FILE, 'r') as f:
		doc = f.read()	
	return discovery.build_from_document(doc, credentials=credentials, http=httplib2.Http())


def get_api_credentials(scope, service_account=True):
	""" Build API client based on oAuth2 authentication """
	# STORAGE = file.Storage(os.environ.get('GOOGLE_VISION_API')) #local storage of oAuth tokens
	STORAGE = file.Storage('youtube_api_key') #local storage of oAuth tokens
	credentials = STORAGE.get()
	if credentials is None or credentials.invalid: #check if new oAuth flow is needed
		if service_account: #server 2 server flow
			# with open(os.environ.get('GOOGLE_VISION_API')) as f:
			with open('youtube_api_key') as f:
				account = json.loads(f.read())
				email = account['client_email']
				key = account['private_key']
			credentials = client.SignedJwtAssertionCredentials(email, key, scope=scope)
			STORAGE.put(credentials)
		else: #normal oAuth2 flow
			CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')
			FLOW = client.flow_from_clientsecrets(CLIENT_SECRETS, scope=scope)
			PARSER = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter, parents=[tools.argparser])
			FLAGS = PARSER.parse_args(sys.argv[1:])
			credentials = tools.run_flow(FLOW, STORAGE, FLAGS)
		
	return credentials


""" read/write utilities """

def read_image(filename):
	return cv2.imread(filename)

def save_image(filename, im):
	cv2.imwrite(filename, cv2.cvtColor(im, cv2.COLOR_RGB2BGR))

def read_image_base64(filename):
	with open(filename, 'rb') as f:
		return b64encode(f.read())


""" OpenCV drawing utilities """

def draw_face(im, annotations):
	faces = []
	for a in annotations:
		if a['detectionConfidence'] > .4:
			try:
				tl_,br_ = draw_box(im, a['fdBoundingPoly']['vertices'])
			except:
				tl_,br_=None

			try:
				joy = a['joyLikelihood']
			except:
				joy=''
			try:
				sad = a['sorrowLikelihood']
			except:
				sad=''
			try:
				angry = a['angerLikelihood']
			except:
				angry = ''
			try:
				suprise=a['surpriseLikelihood']
			except:
				suprise=''

			emotions=[joy,sad,angry,suprise]

			if 'VERY_LIKELY' in emotions:
				emotion = emotions.index('VERY_LIKELY')
			elif 'LIKELY' in emotions:
				emotion = emotions.index('LIKELY')
			elif 'POSSIBLE' in emotions:
				emotion = emotions.index('POSSIBLE')
			else:
				emotion=None
			
			if emotion==0:
				text= "happy"
			elif emotion==1:
				text="sad"
			elif emotion==2:
				text="angry"
			elif emotion==3:
				text="suprised"
			else:
				text="other"
			faces.append(text)
			if im is not None and tl_ is not None:
				draw_text(im, text ,tl_)
			try:
				for landmark in a['landmarks']:
					if im is not None:
						try:
							draw_point(im, landmark['position'])
						except:
							pass
			except:
				pass
	return faces	


def extract_vertices(vertices):
	""" Extract two opposite vertices from a list of 4 (assumption: rectangle) """

	min_x,max_x,min_y,max_y = float("inf"),float("-inf"),float("inf"),float("-inf")

	for v in vertices:
		if v.get('x',min_y) < min_x:
			min_x = v.get('x')
		if v.get('x',max_y) > max_x:
			max_x = v.get('x')
		if v.get('y',min_y) < min_y:
			min_y = v.get('y')
		if v.get('y',max_y) > max_y:
			max_y = v.get('y')
	try:
		v1 = next(v for v in vertices if v.get('x') == min_x and v.get('y') == min_y)
		v2 = next(v for v in vertices if v.get('x') == max_x and v.get('y') == max_y)
	except:
		v1=None
		v2=None

	return v1,v2


def draw_box(im, vertices):
	v1,v2 = extract_vertices(vertices)
	try:
		pt1 = (v1.get('x',0), v1.get('y',0))
		pt2 = (v2.get('x',0), v2.get('y',0))
		cv2.rectangle(im, pt1, pt2, (0,0,255),thickness=4)
	except:
		pt1=None
		pt2=None
	return pt1, pt2

def draw_point(im, position):
	pt = (int(position.get('x',0)), int(position.get('y',0)))
	cv2.circle(im, pt, 3, (0,0,255))
	return pt

def draw_text(im, text,loc):
	font_face = cv2.FONT_HERSHEY_SIMPLEX
	#thickness = 1
	thickness=round(0.002 * (im.shape[0] + im.shape[1]) / 2) + 10
	# for scale in np.arange(20,0,-0.2):
	# 	(w,h),baseline = cv2.getTextSize(text, font_face, scale, thickness)
	# 	if w <= im.shape[1]:
	# 		new_img = cv2.copyMakeBorder(im, 0, baseline*4, 0, 0, cv2.BORDER_CONSTANT, value=0)
	# 		cv2.putText(new_img, text, (baseline*2 +20 ,new_img.shape[0]-baseline +20 ), font_face, 2, (255,255,255), thickness)
	# 		return new_img
	new_img = im
	cv2.putText(new_img, text, loc, font_face, 2.5, (102,255,0), thickness)
	return new_img
