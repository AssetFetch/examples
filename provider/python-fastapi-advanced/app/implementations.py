from . import meta,datablocks
from typing import List

from .assets import Asset

class AssetImplementation:
	pass

class ImplementationListResponse:

	def __init__(self,) -> None:
		self.meta = meta.MetaData(meta.EndpointKind.asset_list)
		self.data = datablocks.DatablockContainer()
		self.assets = List[Asset]