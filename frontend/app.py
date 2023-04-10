import json
import time
import os
from os.path import basename, join
from typing import List
from tqdm import tqdm

import requests
from flask import Flask, jsonify, render_template, request
from PIL import Image

from config import STATIC_IMAGE_FOLDER, STATIC_LAYOUT_FOLDER, MT_ACCESS_TOKEN

app = Flask(__name__)
app.config.update(
	DEBUG = True,
	SECRET_KEY = 'secret_xyz'
)

PREFIX = '/dococr'
PRINTEDIMAGECOUNT=1000
textList=["অসমিয়া","বঙালী","ગુજરાતી","हिंदी","ಕೆನಡಾ","മലയാളം","Manipuri","मराठी","(ଓଡ଼ିଆ","ਪੰਜਾਬੀ","தமிழ்","తెలుగు","اردو"]
def get_NumberOfImages(language: str,imageType: str) -> int:
	print(f'getting all the images for language: {language}')
	path = join(STATIC_IMAGE_FOLDER, language)
	imagesCount = os.listdir(path).__len__()
	imagesCount=imagesCount-1
	if imageType=="Printed":
		return min(imagesCount,PRINTEDIMAGECOUNT)
	else :
		return imagesCount

def get_image_list(language: str) -> List:
	print(f'getting all the images for language: {language}')
	path = join(STATIC_IMAGE_FOLDER, language)
	images = os.listdir(path)
	# removing the 0.jpg from the list as it is only there for git reference
	images = [i for i in images if i.endswith('jpg') and not i.startswith('0')]
	images = [i for i in images if int(i.strip().split('.')[0])<=PRINTEDIMAGECOUNT]
	images = sorted(images, key=lambda x:int(x.strip().split('.')[0]))
	print(images)
	return images


def get_ravi_images(language: str) -> List:
	print(f'getting all the images for language: {language}')
	path = join(STATIC_IMAGE_FOLDER, language)
	images = os.listdir(path)
	# removing the 0.jpg from the list as it is only there for git reference
	images = [i for i in images if i.endswith('jpg') and not i.startswith('0')]
	images = [i for i in images if int(i.strip().split('.')[0])>PRINTEDIMAGECOUNT]
	images = sorted(images, key=lambda x:int(x.strip().split('.')[0]))
	print(images)
	return images


def get_dipti_images() -> List:
	print(f'getting all the images for dipti')
	path = join(STATIC_IMAGE_FOLDER, 'dipti')
	images = os.listdir(path)
	# removing the 0.jpg from the list as it is only there for git reference
	images = [i for i in images if i.endswith('jpg') and not i.startswith('0')]
	images = sorted(images, key=lambda x:int(x.strip().split('.')[0]))
	print(images)
	return images

def get_yojna_images() -> List:
	print(f'getting all the images for dipti')
	path = join(STATIC_IMAGE_FOLDER, 'yojna')
	images = os.listdir(path)
	# removing the 0.jpg from the list as it is only there for git reference
	images = [i for i in images if i.endswith('jpg') and not i.startswith('0')]
	images = sorted(images, key=lambda x:int(x.strip().split('.')[0]))
	print(images)
	return images


@app.route(PREFIX + '/demo', methods=["GET", "POST"])
def demo():
	return render_template('demo.html')

def get_access_token():
	key = 'QUFkb0pmZEpONExLWWVkSlgySUs0YVJqcDU0YTp5Y3pEUmxoQ2twUER6SG1SdTBtQzNnVFJTVm9h'
	url = 'https://sts.choreo.dev/oauth2/token'
	headers = {
		'Authorization': f'Basic {key}'
	}
	data = {
		'grant_type': 'client_credentials'
	}
	r = requests.post(url, headers=headers, data=data, verify=False)
	print(r.text)
	return r.json()['access_token']

def perform_mt(text, lang):
	print(text)
	text = text.strip().split('\n')
	print(len(text))
	token = get_access_token()
	from_lang = lang
	to_lang = 'eng' if lang == 'hin' else 'hin'
	print(f'Performing MT from {from_lang} to {to_lang}')
	url = "https://11fc0468-644c-4cc6-be7d-46b5bffcd914-prod.e1-us-east-azure.choreoapis.dev/aqqz/iiitilmt/1.0.0/onemt"
	headers = {
		'Authorization': f'Bearer {token}',
		'Content-Type': 'application/json',
	}
	ret = []
	for i in tqdm(text):
		payload = json.dumps({
			'text': i,
			'source_language': from_lang,
			'target_language': to_lang
		})
		try:
			r = requests.post(url, headers=headers, data=payload)
			ret.append(r.json()['data'])
		except Exception as e:
			print(e)
			print(r.text)
			pass
	ret = [i.strip() for i in ret]
	return '\n'.join(ret)


@app.route(PREFIX + '/demo_page_mt', methods=['GET', 'POST'])
def demo_page_mt():
	image = request.args.get('image').strip()
	language = request.args.get('language', 'hindi').strip()
	json_path = join(STATIC_LAYOUT_FOLDER, 'demo', image.replace('jpg','json'))
	ret = json.loads(open(json_path, 'r', encoding='utf-8').read())
	text = ret['text']
	text = perform_mt(text, 'eng' if language == 'english' else 'hin')
	ret['text'] = text
	with open(json_path, 'w', encoding='utf-8') as f:
		f.write(json.dumps(ret, indent=4, ensure_ascii=False))
	print(text)
	return render_template(
		'demo_page_mt.html',
		image=image,
		text=text,
		language='hindi' if language == 'english' else 'english',
	)


@app.route(PREFIX + '/demo_page', methods=['GET', 'POST'])
def demo_page():
	print(request.form)
	print(request.files)
	image = request.files['image']
	language = request.form.get('language', 'hindi')
	print(image.filename)
	#commented below line by Vineet
	#image_folder = "/home/krishna/pageocr/frontend/static/images/demo"
	#added below line by Vineet
	image_folder = "/static/images/demo"
	image_path = join(image_folder, image.filename)
	try:
		os.system('rm {}'.format(image_path))
	except:
		pass
	image.save(image_path)
	image = image_path

	r = requests.post(
		'http://10.4.16.103:8881/pageocr/api',
		headers={},
		data={
			'language': language,
			'version': 'v2_robust' if language == 'hindi' else 'v3_robust'
		},
		files=[
			(
				'image',
				(
					basename(image),
					open(image, 'rb'),
					'image/jpeg',
				)
			)
		]
	)
	print(r.status_code)
	layout_location = join(
		STATIC_LAYOUT_FOLDER,
		f'demo/{basename(image).split(".")[0]}.json'
	)
	with open(layout_location, 'w+', encoding='utf-8') as f:
		json.dump(
			r.json(),
			f,
			ensure_ascii=False,
			indent=4
		)
	text = r.json()['text']
	print(text)
	return render_template(
		'demo_page.html',
		image=basename(image),
		text=text,
		language=language,
	)


@app.route(PREFIX + '/', methods=["GET", "POST"])
def index():
	
	return render_template(
		'index.html',
		language_list=zip(os.listdir(STATIC_IMAGE_FOLDER),textList),
	)


@app.route(PREFIX + '/images', methods=['GET'])
def images():
	language = request.args.get('language', 'hindi')
	if language == 'dipti':
		return render_template(
			'dipti_images.html',
			language=language,
			image_list=get_dipti_images(),
		)
	elif language == 'yojna':
		return render_template(
			'yojna_images.html',
			language=language,
			image_list=get_yojna_images(),
		)
	else:
		return render_template(
			'images.html',
			language=language,
			image_list=get_image_list(language),
			ravi_image_list=get_ravi_images(language),
			language_list=zip(os.listdir(STATIC_IMAGE_FOLDER),textList),
		)

@app.route(PREFIX + '/words', methods=['GET'])
def get_all_words():
	image = request.args.get('image').strip()
	language = request.args.get('language', 'hindi').strip()
	image_location = join(STATIC_IMAGE_FOLDER, language, image)
	img = Image.open(image_location)
	width, height = img.width, img.height
	wratio = 350 / width
	hratio = 600 / height
	json_location = join(STATIC_LAYOUT_FOLDER, language, image.replace('jpg','json'))
	a = json.load(open(json_location, 'r'))
	a = a['regions']
	ret = []
	for i in a:
		ret.append({
			'x': int(wratio * i['bounding_box']['x']),
			'y': int(hratio * i['bounding_box']['y']),
			'w': int(wratio * i['bounding_box']['w']),
			'h': int(hratio * i['bounding_box']['h']),
			'text': i['label'].strip(),
		})
	return jsonify(ret)

def get_coordinates(text, start, end):
	text = text.strip()
	while text[start-1] not in ['\n', ' '] and start>0:
		start -= 1
	# line number where selection is: starting from 1
	lineno = len(text[:start].split('\n'))
	# index of the starting word (from 0)
	wstart = text[:start].split('\n')[-1].strip().split(' ')
	if wstart == ['']:
		wstart = 0
	else:
		wstart = len(wstart)
	# index of the ending word (from 0)
	wend = len(text[:end].strip().split('\n')[-1].strip().split(' '))
	return (lineno, wstart, wend)

def combine_bbox(a):
	xmin = min([i['x'] for i in a])
	xmax = max([i['x']+i['w'] for i in a])
	ymin = min([i['y'] for i in a])
	ymax = max([i['y']+i['h'] for i in a])
	return (xmin, ymin, xmax-xmin, ymax-ymin)



@app.route(PREFIX + '/position', methods=['GET'])
def get_word_position():
	image = request.args.get('image').strip()
	language = request.args.get('language', 'hindi').strip()
	start = int(request.args.get('start').strip())
	end = int(request.args.get('end').strip())
	image_location = join(STATIC_IMAGE_FOLDER, language, image)
	img = Image.open(image_location)
	width, height = img.width, img.height
	wratio = 350 / width
	hratio = 600 / height
	json_location = join(STATIC_LAYOUT_FOLDER, language, image.replace('jpg','json'))
	a = json.load(open(json_location, 'r'))
	line, start, end = get_coordinates(a['text'], start, end)
	print(line, start, end)
	a = [i for i in a['regions'] if i['line'] == line]
	print(a)
	a = [i['bounding_box'] for i in a[start:end]]
	print(a)
	a = combine_bbox(a)
	x,y,w,h = a
	x = int(x*wratio)
	y = int(y*hratio)
	w = int(w*wratio)
	h = int(h*hratio)
	print(x,y,w,h)
	a = {
		'x': x,
		'y': y,
		'w': w,
		'h': h
	}
	return jsonify(a)


@app.route(PREFIX + '/page', methods=['GET', 'POST'])
def page():
	image = request.args.get('image').strip()
	language = request.args.get('language', 'hindi').strip()
	imageType=request.args.get('imageType', 'Printed').strip()
	max=get_NumberOfImages(language=language,imageType=imageType)
	nextImage=0;
	prevImage=0;
	imageBaseName=basename(image)
	imageNumber=int(imageBaseName.strip().split('.')[0])
	if imageNumber>1 and (imageNumber!=PRINTEDIMAGECOUNT+1):
		prevImage=imageNumber-1
	if imageNumber<max:
		nextImage=imageNumber+1
	# return render_template(
	# 		'page.html',
	# 		image=image,
	# 		text="text",
	# 		language=language,
	# 		imageType=imageType,
	# 		prevImage=prevImage,
	# 		nextImage=nextImage,
	# 	)
	if int(imageNumber> 1000) or language == 'dipti':
		# either the images are in curated category or language belongs to dipti
		print('hello')
		text = open(join(STATIC_LAYOUT_FOLDER, language, image.replace('jpg', 'json'))).read().strip()
		text = json.loads(text)['text']
		return render_template(
			'page.html',
			image=image,
			text=text,
			type=type,
			language=language,
			imageType=imageType,
			prevImage=prevImage,
			nextImage=nextImage,
		)
	image = join(STATIC_IMAGE_FOLDER, language, image)
	print(image)
	r = requests.post(
		'http://10.4.16.103:8881/pageocr/api',
		headers={},
		data={
			'language': 'hindi' if language == 'yojna' else language
		},
		files=[
			(
				'image',
				(
					basename(image),
					open(image, 'rb'),
					'image/jpeg',
				)
			)
		]
	) 
	print(r.status_code)
	layout_location = join(
		STATIC_LAYOUT_FOLDER,
		language,
		f'{basename(image).split(".")[0]}.json'
	)
	with open(layout_location, 'w+', encoding='utf-8') as f:
		json.dump(
			r.json(),
			f,
			ensure_ascii=False,
			indent=4
		)
	text = r.json()['text']
	print(text)
	return render_template(
		'page.html',
		image=basename(image),
		text=text,
		language=language,
		imageType=imageType,
		prevImage=prevImage,
		nextImage=nextImage,
	)


if __name__ == '__main__':
	app.run(debug = True, host='0.0.0.0', port=5500)
