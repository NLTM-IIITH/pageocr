"""
Page OCR Backend Main API

Author: Krishna Tulsyan (kt.krishna.tulsyan@gmail.com)
"""

import uvicorn

if __name__ == '__main__':
	uvicorn.run('server.app:app', host='0.0.0.0', port=8881, reload=True)
