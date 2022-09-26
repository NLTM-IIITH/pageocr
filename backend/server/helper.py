import base64
import json
import os
import shutil
import uuid
from os.path import basename, dirname, join
from typing import Any, Dict, List

import requests
from fastapi import UploadFile
from PIL import Image

from .config import IMAGE_FOLDER, LANGUAGES
from .models import PageOCRResponse, Region


def call_layout_parser(image_path: str) -> List[Dict[str, int]]:
	"""
	function to the call the layout parser API

	@returns the list of the regions of the word level parser
	"""
	url = "http://10.4.16.103:8888/layout"
	files=[
		(
			'images',
			(
				basename(image_path),		# filename
				open(image_path,'rb'),		# file object
				'image/jpeg'				# file mimetype
			)
		)
	]
	response = requests.post(
		url,
		headers={},
		data={},
		files=files
	)
	return response.json()[0]['regions']


def crop_regions(image_path: str, regions: List[Dict[str, Any]]) -> str:
	"""
	crop the original image given the regions output of the layout parser
	and saves each of the word in a separate image inside folder

	@returns the path where cropped images are saved
	"""
	# folder to save all the word level cropped images
	ret = join(
		dirname(image_path),
		basename(image_path).strip().split('.')[0],
	)
	os.makedirs(ret)
	img = Image.open(image_path)
	bboxes = [i['bounding_box'] for i in regions]
	bboxes = [(i['x'], i['y'], i['x']+i['w'], i['y']+i['h']) for i in bboxes]
	for idx, bbox in enumerate(bboxes):
		with open(join(ret, '{}.jpg'.format(idx)), 'wb+') as f:
			img.crop(bbox).save(f)
	return ret


def load_model(language: str):
	"""
	Calls the ocr api load model endpoint with the language param
	"""
	url = f'http://bhasha.iiit.ac.in/ocr/v0/load?modality=printed&language={language}'
	response = requests.post(url)
	return response.ok


def perform_ocr(path: str, language: str) -> List[str]:
	"""
	call the ocr API on all the images inside the path folder

	Because when selecting the language from the index page. we call the
	the concerned ocr model is loaded into the beforehand, so we specify
	the preloaded=true by default in the ocr api url
	"""
	a = os.listdir(path)
	a = sorted(a, key=lambda x:int(x.strip().split('.')[0]))
	a = [join(path, i) for i in a if i.endswith('jpg')]
	a = [base64.b64encode(open(i, 'rb').read()).decode() for i in a]
	print(list(map(len, a)))
	ocr_request = {
		'imageContent': a,
		'modality': 'printed',
		'language': LANGUAGES[language],
		'version': 'v2',
	}
	url = "http://bhasha.iiit.ac.in/ocr/infer"
	response = requests.post(url, headers={
		'Content-Type': 'application/json'
	}, data=json.dumps(ocr_request))
	ret = response.json()
	ret = [i['text'] for i in ret]
	return ret


def format_ocr_output(ocr: List[str], regions: List[Dict[str, Any]]) -> str:
	"""
	takes the word level ocr output for all the words and corresponding
	regions extracted from the layout-parser and constructs the
	proper output string.

	@returns the final page level ocr output with appropriate '\n'
	"""
	ret = []
	lines = [i['line'] for i in regions]
	assert len(lines) == len(ocr)
	prev_line = lines[0]
	tmp_line = []
	for line, text in zip(lines, ocr):
		if line == prev_line:
			tmp_line.append(text)
		else:
			prev_line = line
			ret.append(' '.join(tmp_line))
			tmp_line = [text]
	# this is so that the last line is also included in the ret
	ret.append(' '.join(tmp_line))
	ret = [i.strip() for i in ret]
	ret = '\n'.join(ret).strip()
	regions = [Region(**i) for i in regions]
	return PageOCRResponse(
		text=ret,
		regions=regions
	)


def save_uploaded_image(image: UploadFile) -> str:
	"""
	function to save the uploaded image to the disk

	@returns the absolute location of the saved image
	"""
	location = join(IMAGE_FOLDER, '{}.{}'.format(
		str(uuid.uuid4()),
		image.filename.strip().split('.')[-1]
	))
	with open(location, 'wb+') as f:
		shutil.copyfileobj(image.file, f)
	return location
