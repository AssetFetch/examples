
from typing import Dict, List
import pathlib
import yaml

from . import datablocks,templates,config

class Asset:
	def __init__(self,id:str,title:str,description:str,license_spdx:str,author:str,author_uri:str,kind:str) -> None:

		parameters = []

		if kind == "material":
			parameters.append(templates.HttpParameter(
				type=templates.HttpParameterType.select,
				id="resolution",
				title="Resolution",
				choices=[templates.HttpParameterChoice("1K","1"),templates.HttpParameterChoice("2K","2")],
				mandatory=True
			))
			parameters.append(templates.HttpParameter(
				type=templates.HttpParameterType.select,
				id="format",
				title="Format",
				choices=[templates.HttpParameterChoice("JPG","jpg"),templates.HttpParameterChoice("PNG","png")],
				mandatory=True
			))
		
		if kind == "model":
			parameters.append(templates.HttpParameter(
				type=templates.HttpParameterType.select,
				id="resolution",
				title="Resolution",
				choices=[templates.HttpParameterChoice("1K","1"),templates.HttpParameterChoice("2K","2")],
				mandatory=True
			))
			parameters.append(templates.HttpParameter(
				type=templates.HttpParameterType.select,
				id="lod",
				title="Level of Detail",
				choices=[templates.HttpParameterChoice("Low","low"),templates.HttpParameterChoice("Medium","medium")],
				mandatory=True
			))

		self.id = id
		self.data = datablocks.DataField([
			datablocks.ImplementationListQueryBlock(uri=f"{config.API_URL}/implementation_list/{self.id}",method=templates.HttpMethod.GET,parameters = parameters),
			datablocks.TextBlock(title=title,description=description),
			datablocks.LicenseBlock(license_spdx,None),
			datablocks.PreviewImageThumbnailBlock(
				f"{id} Thumbnail",
				{
					"256":f"{config.API_URL}/thumbnail/{id}"
				}),
			datablocks.AuthorsBlock([
				datablocks.SingularAuthor(author,author_uri,None)
			])
		])