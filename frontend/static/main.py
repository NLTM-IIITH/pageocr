import json
import os
from os.path import abspath, basename, join
from typing import List, Tuple

from PIL import Image


def sort_words(boxes):
    """
    boxes is a list of tuples. in top-left and bottom-right format.
    Sort boxes - (left, top, right, bottom) from left to right, top to bottom.
    the function returns a list of lines each line containing a list of tuple bbox.
    """
    mean_height = sum([y2 - y1 for _, y1, _, y2, _ in boxes]) / len(boxes)

    current_line = boxes[0][1]
    lines = []
    tmp_line = []
    for box in boxes:
        if box[1] > current_line + mean_height:
            lines.append(tmp_line)
            tmp_line = [box]
            current_line = box[1]            
            continue
        tmp_line.append(box)
    lines.append(tmp_line)

    for line in lines:
        line.sort(key=lambda box: box[0])

    return lines

def convert_bbox(a: List) -> Tuple[int]:
    x = [i[0] for i in a]
    y = [i[1] for i in a]
    return (min(x), min(y), max(x), max(y))

def layout_format(a, line):
	return {
		'bounding_box': {
			'x': a[0],
			'y': a[1],
			'w': a[2]-a[0],
			'h': a[3]-a[1],
		},
		'label': a[4],
		'line': line
	}

def copy_image(src, dest):
	"""
	converts the tif to jpg and transfer to the dest
	"""
	Image.open(src).save(dest, 'JPEG')

def get_text(regions):
	ret = []
	lines = [i['line'] for i in regions]
	ocr = [i['label'] for i in regions]
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
	return {
		'text': ret,
		'regions': regions,
	}
	# regions = [Region(**i) for i in regions]
	# return PageOCRResponse(
	# 	text=ret,
	# 	regions=regions
	# )

def process_page(a, counter, lang):
	print(lang, counter)
	imagepath = join('images', lang, f'{counter}.jpg')
	layoutpath = join('layouts', lang, f'{counter}.json')
	print(imagepath, layoutpath)
	copy_image(a['imagePath'], abspath(imagepath))
	bbox_list = []
	for i in a['regions']:
		if 'modelPrediction' in i and len(i['modelPrediction']) == 4:
			bbox = i['modelPrediction']
		# elif 'groundTruth' in i and len(i['groundTruth']) == 4:
		# 	bbox = i['groundTruth']
		else:
			continue
		bbox = convert_bbox(bbox)
		assert len(bbox) == 4
		bbox = list(bbox)
		bbox.append(i['ocr'])
		bbox_list.append(bbox)
	bbox_list = sort_words(bbox_list)
	regions = []
	for i,v in enumerate(bbox_list):
		for x in v:
			regions.append(layout_format(x, i+1))
	layoutjson = get_text(regions)
	with open(layoutpath, 'w', encoding='utf-8') as f:
		f.write(json.dumps(layoutjson, indent=4, ensure_ascii=False))


lang = 'punjabi'

jsonpath = join('new_json', f'{lang}_new.json')
a = open(jsonpath, 'r').read().strip()
a = json.loads(a)
counter = 1001

for pageid in a:
	process_page(a[pageid], counter, lang)
	counter += 1
