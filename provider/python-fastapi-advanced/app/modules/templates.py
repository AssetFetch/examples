from enum import StrEnum
from typing import Dict, List

from fastapi.encoders import jsonable_encoder

# Templates for the meta field
class EndpointKind(StrEnum):
	initialization = "initialization"
	asset_list = "asset_list"
	implementation_list = "implementation_list"
	unlock = "unlock"
	unlocked_datablocks="unlocked_datablocks"
	connection_status = "connection_status"


class MetaField:
	def __init__(self,kind : EndpointKind,message : str = "OK",version : str = "0.4") -> None:
		self.kind :EndpointKind = kind
		self.message :str = message
		self.version :str = version

# HTTP query related templates
class HttpMethod(StrEnum):
	GET = "get"
	POST = "post"

class HttpParameterType:
	text = "text"
	boolean = "boolean"
	hidden = "hidden"
	select = "select"
	multiselect = "multiselect"

class HttpParameterChoice:
	def __init__(self,title,value) -> None:
		self.title = title
		self.value = value

class HttpParameter:
	def __init__(self, type : HttpParameterType, id : str, title : str, default : str = "",choices : List[HttpParameterChoice]|None = None,):
		self.type = type
		self.id = id
		self.title = title
		self.default = default
		self.choices = choices

class FixedQuery:
	def __init__(self,uri : str, method : HttpMethod, payload : Dict[str,str] ) -> None:
		self.uri : str = uri
		self.method : HttpMethod = method
		self.payload : Dict[str,str] = payload

class VariableQuery:
	def __init__(self,uri : str, method : HttpMethod, parameters : List[HttpParameter]) -> None:
		self.uri = uri
		self.method = method
		self.parameters = parameters