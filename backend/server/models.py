from typing import Dict, List

from pydantic import BaseModel


class Region(BaseModel):
	bounding_box: Dict[str, int]
	label: str
	line: int


class PageOCRResponse(BaseModel):
	text: str
	regions: List[Region]
