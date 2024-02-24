
from typing import Dict, List
import pathlib
import yaml

from . import meta,datablocks,config,queries

class Asset:
	def __init__(self,asset_yaml:str) -> None:

		# Read the data file for this asset
		with open(asset_yaml, 'r') as file:
			about_asset = yaml.safe_load(file)

		self.name = pathlib.Path(asset_yaml).parent.name
		self.data = datablocks.DatablockContainer([
			datablocks.ImplementationListQueryBlock(uri="",method=queries.HttpMethod.GET,payload={}),
			datablocks.TextBlock(title=about_asset.title,description=about_asset.description),
			datablocks.LicenseBlock(about_asset.license_spdx,None),
			datablocks.AuthorsBlock([
				datablocks.SingularAuthor(about_asset.author,about_asset.author_uri,None)
			])
		])

class AssetListResponse:
	def __init__(self,assets:List[Asset]) -> None:
		self.meta = meta.MetaData(meta.EndpointKind.asset_list)
		self.data = datablocks.DatablockContainer()
		self.assets = List[Asset]