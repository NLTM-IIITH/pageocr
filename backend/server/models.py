from typing import List, Optional

from pydantic import BaseModel, Field


class PageOCRResponse(BaseModel):
	text: str