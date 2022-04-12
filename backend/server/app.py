from fastapi import FastAPI, File, UploadFile
from fastapi.responses import PlainTextResponse

from .helper import *
from .models import *

app = FastAPI(
	title='PageOCR Backend API',
	description='',
	docs_url='/',
)


@app.post('/pageocr', tags=['Page OCR'], response_class=PlainTextResponse)
async def perform_page_level_ocr(
	image: UploadFile = File(...)
) -> str:
	image_path = save_uploaded_image(image)
	print(image_path)
	regions = call_layout_parser(image_path)
	print(regions)
	path = crop_regions(image_path, regions)
	print(path)
	ocr_output = perform_ocr(path)
	print(len(regions))
	print(len(ocr_output))
	return format_ocr_output(ocr_output, regions)
