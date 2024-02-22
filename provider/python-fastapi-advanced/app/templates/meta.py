from enum import Enum

class AfEndpointKind(Enum):
	initialization = "initialization"
	asset_list = "asset_list"
	implementation_list = "implementation_list"

class AfMetaData:
	def __init__(self,kind : AfEndpointKind,message : str = "OK",version : str = "0.2.0-dev") -> None:
		self.kind :AfEndpointKind = kind
		self.message :str = message
		self.version :str = version