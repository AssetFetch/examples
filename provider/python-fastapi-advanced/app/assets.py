
from typing import Dict
from . import datablock,query,config
import pathlib

class AssetImplementation:
	pass

class Asset:
	def __init__(self,name:str,directory:pathlib.Path) -> None:
		self.name = name
		self.directory = directory

		self.implementation

		self.register_datablock(
			datablock.ImplementationListQueryBlock(f"{config.API_URL}/implementation_list/{self.name}",query.HttpMethod.GET)
		)

	def set_datablock(self,block:datablock.Datablock):
		self.data[block.block_name] = block

	def get_data_block(self,block_name:str) -> any|None:
		return self.data[block_name]