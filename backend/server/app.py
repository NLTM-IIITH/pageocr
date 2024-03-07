from typing import Optional

from fastapi import FastAPI, File, Form, UploadFile

from .helper import *
from .models import *

app = FastAPI(
	title='PageOCR Backend API',
	description='',
	docs_url='/pageocr/docs',
	openapi_url='/pageocr/openapi.json',
)


@app.post('/pageocr/api', tags=['Page OCR'], response_model=PageOCRResponse)
async def perform_page_level_ocr(
	image: UploadFile = File(...),
	language: Optional[str] = Form('hindi'),
	version: Optional[str] = Form('v4_robust'),
	modality: Optional[str] = Form('printed'),
	layout_model: Optional[str] = Form('v2_doctr'),
	postprocess: Optional[bool] = Form(False),
):
	print(language, version, modality, layout_model)
	image_path = save_uploaded_image(image)
	img = Image.open(image_path)
	print(f'Saved the image at {image_path}')
	regions = call_layout_parser(image_path, layout_model, language)
	# if modality == 'handwritten' or modality == 'scenetext' or layout_model == 'none':
	# 	regions = [{
	# 		'bounding_box': {'x': 1, 'y': 1, 'w': img.width-1, 'h': img.height-1},
	# 		'order': -1,
	# 		'label': '',
	# 		'line': 1
	# 	}]
	# else:
	# 	regions = call_layout_parser(image_path, layout_model, language)
	print(f'{len(regions)} word regions detected by layout-parser')
	path = crop_regions(image_path, regions)
	print(f'Saved the cropped word images at: {path}')
	ocr_output = perform_ocr(path, language, version, modality, postprocess)
	print('Got the OCR Output')
	ret = format_ocr_output(ocr_output, regions)
	print('Formatted the OCR Output')
	return ret


@app.post('/load_ocr', tags=['Helper'])
async def load_ocr_model(
	language: str
):
	"""
	This is the API endpoint to load the given language ocr model to memory
	this endpoint directly calls the "/ocr/v0/load"
	"""
	print(f'Loading the {language} OCR model.')
	load_model(language)
	return {'detail': 'Model loaded'}
