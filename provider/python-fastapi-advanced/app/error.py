from fastapi import Request,HTTPException,status
from fastapi.responses import JSONResponse

from . import meta

class AssetFetchException(Exception):
	def __init__(self, endpoint_kind: meta.EndpointKind,message:str,status_code:status):
		self.endpoint_kind = endpoint_kind
		self.message = message
		self.status_code = status_code

def assetfetch_exception_handler(request: Request, exc: AssetFetchException):
	return JSONResponse(status_code=exc.status_code, content=meta.MetaData(kind=exc.endpoint_kind,message=exc.message))
