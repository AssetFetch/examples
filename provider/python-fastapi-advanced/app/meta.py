from enum import Enum

class EndpointKind(Enum):
	initialization = "initialization"
	asset_list = "asset_list"
	implementation_list = "implementation_list"

class MetaData:
	def __init__(self,kind : EndpointKind,message : str = "OK",version : str = "0.2.0-dev") -> None:
		self.kind :EndpointKind = kind
		self.message :str = message
		self.version :str = version