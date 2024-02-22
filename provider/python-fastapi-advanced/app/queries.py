from enum import Enum
from typing import Dict, List

class HttpMethod(Enum):
	GET = "get"
	POST = "post"

class HttpParameterType:
	text = "text"
	boolean = "boolean"
	hidden = "hidden"
	select = "select"
	multiselect = "multiselect"

class HttpParameter:
    def __init__(self, type : HttpParameterType, name : str, title : str, default : str = "", mandatory : bool = False, choices : List[str]=[], delimiter : str=','):
        self.type = type
        self.name = name
        self.title = title
        self.default = default
        self.mandatory = mandatory
        self.choices = choices
        self.delimiter = delimiter

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

