import json
import os
from os.path import basename, join
from typing import List

import requests
from flask import Flask, jsonify, render_template, request
from PIL import Image

from config import STATIC_IMAGE_FOLDER, STATIC_LAYOUT_FOLDER

app = Flask(__name__)
app.config.update(
	DEBUG = True,
	SECRET_KEY = 'secret_xyz'
)


def get_image_list(language: str) -> List:
	print(f'getting all the images for language: {language}')
	path = join(STATIC_IMAGE_FOLDER, language)
	images = os.listdir(path)
	# removing the 0.jpg from the list as it is only there for git reference
	images = [i for i in images if i.endswith('jpg') and not i.startswith('0')]
	images = sorted(images, key=lambda x:int(x.strip().split('.')[0]))
	print(images)
	return images



@app.route('/', methods=["GET", "POST"])
def index():
	return render_template(
		'index.html',
		language_list=os.listdir(STATIC_IMAGE_FOLDER)
	)


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


@app.route('/position', methods=['GET'])
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


@app.route('/page', methods=['GET', 'POST'])
def page():
	image = request.args.get('image').strip()
	language = request.args.get('language', 'hindi').strip()
	image = join(STATIC_IMAGE_FOLDER, language, image)
	print(image)
	r = requests.post(
		'http://10.4.16.103:8881/pageocr',
		headers={},
		data={
			'language': language
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
	)


if __name__ == '__main__':
	app.run(debug = True, host='0.0.0.0', port=5500)
