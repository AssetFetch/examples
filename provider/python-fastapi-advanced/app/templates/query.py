from enum import Enum
from typing import Dict, List

class AfHttpMethod(Enum):
	GET = "get"
	POST = "post"

class AfHttpParameterType:
	text = "text"
	boolean = "boolean"
	hidden = "hidden"
	select = "select"
	multiselect = "multiselect"

class AfHttpParameter:
    def __init__(self, type : AfHttpParameterType, name : str, title : str, default : str = "", mandatory : bool = False, choices : List[str]=[], delimiter : str=','):
        self.type = type
        self.name = name
        self.title = title
        self.default = default
        self.mandatory = mandatory
        self.choices = choices
        self.delimiter = delimiter

class AfFixedQuery:
	def __init__(self,uri : str, method : AfHttpMethod, payload : Dict[str,str] ) -> None:
		self.uri : str = uri
		self.method : AfHttpMethod = method
		self.payload : Dict[str,str] = payload

class AfVariableQuery:
	def __init__(self,uri : str, method : AfHttpMethod, parameters : List[AfHttpParameter]) -> None:
		self.uri = uri
		self.method = method
		self.parameters = parameters

