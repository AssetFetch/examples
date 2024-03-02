from typing import List
from . import datablocks

class AssetImplementationComponent:
	def __init__(self,id:str,data:List[datablocks.Datablock]) -> None:
		self.id : str = id
		self.data : datablocks.DataField = datablocks.DataField(data)

class AssetImplementation:
	def __init__(self,id:str,data:List[datablocks.Datablock],components:List[AssetImplementationComponent]) -> None:
		self.id : str = id
		self.data : datablocks.DataField = datablocks.DataField(data)
		self.components : List[AssetImplementationComponent] = components