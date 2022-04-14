import os

import requests
from flask import Flask, render_template, request

app = Flask(__name__)
app.config.update(
	DEBUG = True,
	SECRET_KEY = 'secret_xyz'
)


@app.route('/', methods=["GET", "POST"])
def index():
	images_path = '/home/krishna/pageocr/frontend/static/images'
	images = os.listdir(images_path)
	images = [i for i in images if i.endswith('jpg')]
	images = sorted(images, key=lambda x:int(x.strip().split('.')[0]))
	print(images)
	return render_template('index.html', images=images)


@app.route('/page', methods=['GET', 'POST'])
def page():
	image = request.args.get('image').strip()
	image = os.path.join('/home/krishna/pageocr/frontend/static/images/',image)
	print(image)
	r = requests.post(
		'http://10.4.16.103:8881/pageocr',
		headers={},
		data={},
		files=[
			(
				'image',
				(
					os.path.basename(image),
					open(image, 'rb'),
					'image/jpeg',
				)
			)
		]
	)
	print(r.status_code)
	text = r.json()['text']
	print(text)
	return render_template('page.html', image=os.path.basename(image), text=text)


if __name__ == '__main__':
	app.run(debug = True, host='0.0.0.0', port=5500)
