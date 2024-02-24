from typing import List
from . import datablocks,templates

class AssetImplementationComponent:
	def __init__(self,name:str,data:List[datablocks.Datablock]) -> None:
		self.name : str = name
		self.data : datablocks.DataField = datablocks.DataField(data)

class AssetImplementation:
	def __init__(self,name:str,data:List[datablocks.Datablock] = [],components:List[AssetImplementationComponent] = []) -> None:
		self.name : str = name
		self.data : datablocks.DataField = datablocks.DataField(data)
		self.components : List[AssetImplementationComponent] = components