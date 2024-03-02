
from typing import Dict, List
import pathlib
import yaml

from . import datablocks,templates,config

class Asset:
	def __init__(self,asset_yaml:str) -> None:

		with open(asset_yaml, 'r') as file:
			about_asset = yaml.safe_load(file)

		self.id = pathlib.Path(asset_yaml).parent.name
		self.data = datablocks.DataField([
			datablocks.ImplementationListQueryBlock(uri=f"{config.API_URL}/implementation_list/{self.id}",method=templates.HttpMethod.GET,parameters = []),
			datablocks.TextBlock(title=about_asset['title'],description=about_asset['description']),
			datablocks.LicenseBlock(about_asset['license_spdx'],None),
			datablocks.AuthorsBlock([
				datablocks.SingularAuthor(about_asset['author'],about_asset['author_uri'],None)
			])
		])