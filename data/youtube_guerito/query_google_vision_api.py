from datetime import date
import datetime
import json
from webbrowser import get
from google.cloud.vision_v1.types.image_annotator import AnnotateImageRequest, AnnotateImageResponse
from numpy.core.fromnumeric import shape
from numpy.core.numeric import NaN
from numpy.lib.arraysetops import unique
from skimage.util import dtype
from functions_for_google_vision_api import (get_vision_api, read_image, read_image_base64, save_image, draw_face, draw_box, draw_text)
from skimage import io
import os
from google.cloud import vision_v1
from google.cloud import vision
from google.cloud.vision_v1 import types
import cv2
import pandas as pd
import numpy as np
import itertools
import time
import random

#####################################################################

import httplib2
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.environ.get('GOOGLE_VISION_API')

DISCOVERY_URL='https://{api}.googleapis.com/$discovery/rest?version={apiVersion}'

def get_vision_service():
    credentials = GoogleCredentials.get_application_default()
    return discovery.build('vision', 'v1', credentials=credentials,
                           discoveryServiceUrl=DISCOVERY_URL)	


def main(video_id, inputfile):
	service = get_vision_service()
	outputfile= "C:/Users/merre/Desktop/ws/data/youtube_guerito/output_images/thumbnail_" +inputfile[inputfile.rfind('/', 0, inputfile.rfind('/'))+1:inputfile.rfind('/')] + ".jpg"

	batch_request=[
    {
      "features": [
        {
          "maxResults": 50,
          "type": "FACE_DETECTION"
        },
        {
          "maxResults": 50,
          "type": "LABEL_DETECTION"
        },
        {
          "maxResults": 20,
          "type": "SAFE_SEARCH_DETECTION"
        },
        {
          "maxResults": 50,
          "type": "TEXT_DETECTION"
        }
      ],
		"image": {
				"source": {
				"imageUri": inputfile
				}
			}
    }
	]
	request = service.images().annotate(body={
		'requests': batch_request,
		})
	time.sleep(random.random()*4)
	response = request.execute()

	inputfile,labels,faces,texts,adult,medical,racy,spoof,violence = show_results(inputfile, response, outputfile)
	vars_list = [video_id,inputfile,labels,faces,texts,adult,medical,racy,spoof,violence]
	i=0
	for v in vars_list:
		if type(v) == np.ndarray:
			v = v.tolist()
			vars_list[i]=v
		i += 1
	return vars_list


def show_results(inputfile, data, outputfile):

	#read original file
	im = io.imread(inputfile)

	#draw face, boxes and text for each response
	faces=[]
	labels=[]
	texts=[]
	#dict_keys = data.keys()
	for r in data['responses']:
		
		if 'faceAnnotations' in r:
			faces = draw_face(im, r['faceAnnotations'])
		
		if 'labelAnnotations' in r:
			for label in r['labelAnnotations']:
				if label['score'] > .6:
					try:
						labels.append(label['description'])
					except:
						labels=labels
		
		if 'textAnnotations' in r:
			for a in r['textAnnotations']:
				if a['description'] != '':
					try:
						texts.append(a['description'])
					except:
						texts=texts
		
		if 'safeSearchAnnotation' in r:
			try:
				adult = r['safeSearchAnnotation']["adult"]
			except:
				adult=''
			try:
				medical = r['safeSearchAnnotation']["medical"]
			except:
				medical=''
			try:
				racy = r['safeSearchAnnotation']["racy"]
			except:
				racy=''
			try:	
				spoof = r['safeSearchAnnotation']["spoof"]
			except:
				spoof=''
			try:
				violence = r['safeSearchAnnotation']["violence"]
			except:
				violence=''
	
	labels=unique(labels)
	texts=unique(texts)
		#save to output file
	save_image(outputfile, im)

	return inputfile,labels,faces,texts,adult,medical,racy,spoof,violence

files= ["jan_el_wero.txt",
"nate's_adventures.txt",
"nathan_seastrand.txt",
"rusos_reaccionan.txt",
"superholly.txt",
"vlog_güero.txt",
"wero_wero_tv.txt",
"american_boy.txt",
"dustin_luke.txt",
"el_gringo.txt",
"el_güerito.txt",
"ford_quarterman.txt",
"gringa_reacciona.txt"]

vid_ids=[]
vid_thumb_urls=[]
for file in files:
	videos_loop= pd.read_csv(file)
	vid_ids.append(list(videos_loop[pd.to_datetime(videos_loop["upload_date"])>datetime.datetime(2012,7,1,0,0,0,0)]["video_id"]))
	vid_thumb_urls.append(list(videos_loop[pd.to_datetime(videos_loop["upload_date"])>datetime.datetime(2012,7,1,0,0,0,0)]["thumbnail_url"]))
	
vid_ids=list(itertools.chain(*vid_ids))
vid_thumb_urls=list(itertools.chain(*vid_thumb_urls))
print(len(vid_ids))
df = pd.DataFrame(columns=['video_id','thumbnail_url', 'labels','faces','texts','adult','medical','racy','spoof','violence'])
ii = 0

for i in range(1299,len(vid_ids)):
	if vid_thumb_urls[i] is not NaN:
		time.sleep(11)
		try:
			df.loc[len(df)] = main(video_id=vid_ids[i],inputfile=vid_thumb_urls[i])
			ii += 1

		except:
			pass
		if ii % 10 == 0 or i==len(vid_ids)-1 or i==len(vid_ids):
			df.to_csv('thumbnail_data_'+str(datetime.datetime.now()).replace('-','').replace(' ','_').replace(':','-')+'.txt', header=True, index=None, mode='w')
			print(i,"Percent complete:",round(i/len(vid_ids),3))

