import json
import os
from os.path import basename, join

import requests
from flask import Flask, render_template, request

from config import STATIC_IMAGE_FOLDER, STATIC_LAYOUT_FOLDER

app = Flask(__name__)
app.config.update(
	DEBUG = True,
	SECRET_KEY = 'secret_xyz'
)


@app.route('/', methods=["GET", "POST"])
def index():
	images = os.listdir(STATIC_IMAGE_FOLDER)
	# removing the 0.jpg from the list as it is only there for git reference
	images = [i for i in images if i.endswith('jpg') and not i.startswith('0')]
	images = sorted(images, key=lambda x:int(x.strip().split('.')[0]))
	print(images)
	return render_template('index.html', images=images)


@app.route('/page', methods=['GET', 'POST'])
def page():
	image = request.args.get('image').strip()
	language = request.args.get('language', 'hindi').strip()
	image = join(STATIC_IMAGE_FOLDER, image)
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
	return render_template('page.html', image=basename(image), text=text)


if __name__ == '__main__':
	app.run(debug = True, host='0.0.0.0', port=5500)
