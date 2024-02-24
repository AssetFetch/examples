from fastapi import Request,HTTPException,status
from fastapi.responses import JSONResponse

from . import templates

class AssetFetchException(Exception):
	def __init__(self, endpoint_kind: templates.EndpointKind,message:str,status_code:status):
		self.endpoint_kind = endpoint_kind
		self.message = message
		self.status_code = status_code

def assetfetch_exception_handler(request: Request, exc: AssetFetchException):
	return JSONResponse(
		status_code=exc.status_code,
		content={
			"meta":templates.MetaField(kind=exc.endpoint_kind,message=exc.message).__dict__
		})
