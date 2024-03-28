

from enum import Enum, StrEnum
import os
import pathlib
from typing import Dict, List
from abc import ABC,abstractmethod

from . import templates,config,users

class Datablock:
	"""Abstract class that all datablocks must implement.
	It ensures that every datablock has a block_name property
	"""
	@property
	@abstractmethod
	def block_name(self):
		pass

class DataField(Dict[str,Datablock]):
	def __init__(self,blocks : List[Datablock]) -> None:
		for b in blocks:
			self.set_block(b)

	def set_block(self,block:Datablock):
		self[block.block_name] = block

### DATABLOCKS

class ImplementationListQueryBlock(templates.VariableQuery,Datablock):
	block_name = "implementation_list_query"

class AssetListQueryBlock(templates.VariableQuery,Datablock):
	block_name = "asset_list_query"

class UnlockableDataQuery(templates.VariableQuery,Datablock):
	block_name = "unlockable_data_query"

class TextBlock(Datablock):
	block_name = "text"
	def __init__(self,title : str, description : str = None) -> None:
		self.title = title
		self.description = description

class SingularHeader:
	def __init__(self,name : str, is_required : bool, is_sensitive: bool, title:str, acquisition_uri : str, acquisition_uri_title : str) -> None:
		self.name = name
		self.is_required = is_required
		self.is_sensitive = is_sensitive
		self.is_required = is_required
		self.title = title
		self.acquisition_uri = acquisition_uri
		self.acquisition_uri_title = acquisition_uri_title

class ProviderConfigurationBlock(Datablock):
	block_name = "provider_configuration"
	def __init__(self,headers:List[SingularHeader],connection_status_query:templates.FixedQuery) -> None:
		self.headers = headers
		self.connection_status_query = connection_status_query
		super().__init__()

class UnlockBlock(Datablock):
	block_name = "unlock"
	def __init__(self,locked:bool,price:float,unlock_query:templates.FixedQuery) -> None:
		self.locked = locked
		self.price = price
		self.unlock_query = unlock_query
		super().__init__()

class SingularWebReference:
	def __init__(self,title:str,uri:str) -> None:
		self.title = title
		self.uri = uri

class WebReferencesBlock(List[SingularWebReference],Datablock):
	block_name = "web_references"

class BrandingBlock(Datablock):
	block_name = "branding"
	def __init__(self,color_accent:str,logo_square_uri:str,logo_wide_uri:str,banner_uri:str) -> None:
		self.color_accent = color_accent
		self.logo_square_uri = logo_square_uri
		self.logo_wide_uri = logo_wide_uri
		self.banner_uri = banner_uri

class LicenseBlock(Datablock):
	block_name = "license"
	def __init__(self,license_spdx : str,license_uri:str) -> None:
		self.license_spdx = license_spdx
		self.license_uri = license_uri

class SingularAuthor:
	def __init__(self,name:str,uri:str,role:str) -> None:
		self.name=name
		self.uri = uri
		self.role = role

class AuthorsBlock(Datablock,List[SingularAuthor]):
	block_name = "authors"

class ObjUpAxis(StrEnum):
	PLUS_Y = "+y"
	PLUS_Z = "+z"

class ObjFormatBlock(Datablock):
	block_name = "format.obj"
	def __init__(self,up_axis:ObjUpAxis,use_mtl:bool) -> None:
		super().__init__()
		self.up_axis : ObjUpAxis=up_axis
		self.use_mtl : bool = use_mtl

class FileFetchDownloadBlock(Datablock,templates.FixedQuery):
	block_name = "file_fetch.download"
	def __init__(self, uri: str, method: templates.HttpMethod, payload: Dict[str, str]) -> None:
		super().__init__(uri, method, payload)

class BehaviorStyle(StrEnum):
	FILE_ACTIVE="file_active"
	FILE_PASSIVE="file_passive"
	ARCHIVE="archive"
class FileInfoBlock(Datablock):
	block_name = "file_info"
	def __init__(self,local_path:str,length:int,extension:str,behavior:BehaviorStyle) -> None:
		super().__init__()
		self.local_path = local_path
		self.length = length
		self.extension = extension
		self.behavior = behavior

def file_fetch_download_block_from_path(file_path : pathlib.Path) -> FileFetchDownloadBlock :
		relative_to_asset_dir : str = file_path.relative_to(config.ASSET_DIRECTORY)

		return FileFetchDownloadBlock(
			f"{config.API_URL}/static/{relative_to_asset_dir}",
			templates.HttpMethod.GET,
			{}
		)

def file_info_block_from_path(file_path : pathlib.Path,local_path:str,behavior:BehaviorStyle) -> FileInfoBlock:
	relative_to_asset_dir : str = file_path.relative_to(config.ASSET_DIRECTORY)

	return FileInfoBlock(
		local_path=local_path,
		length=os.stat(file_path).st_size,
		extension="".join(file_path.suffixes),
		behavior=behavior
	)


class LooseMaterialMapName(StrEnum):
	albedo = "albedo"
	roughness = "roughness"
	metallic = "metallic"
	diffuse = "diffuse"
	glossiness = "glossiness"
	specular = "specular"
	height = "height"
	normal_plus_y = "normal+y"
	normal_minus_y = "normal-y"
	opacity = "opacity"
	ambient_occlusion = "ambient_occlusion"
	emission = "emission"

class LooseMaterialColorSpace(StrEnum):
	SRGB = "srgb"
	LINEAR = "linear"

class LooseMaterialApplyElement:
	def __init__(self,material_name:str,apply_selectively_to:str|None) -> None:
		self.material_name : str = material_name
		self.apply_selectively_to : str|None = apply_selectively_to

class LooseMaterialDefineBlock(Datablock):
	block_name="loose_material_define"
	def __init__(self,material_name:str,map:LooseMaterialMapName,colorspace:LooseMaterialColorSpace) -> None:
		super().__init__()
		self.material_name :str = material_name
		self.map : LooseMaterialMapName = map
		self.colorspace : LooseMaterialColorSpace = colorspace

class LooseMaterialApplyBlock(Datablock,List[LooseMaterialApplyElement]):
	block_name="loose_material_apply"
	def __init__(self,elements : List[LooseMaterialApplyElement]) -> None:
		super().__init__()
		for e in elements:
			self.append(e)

class PreviewImageThumbnailBlock(Datablock):
	block_name="preview_image_thumbnail"
	def __init__(self,alt:str,uris:Dict[int,str]) -> None:
		super().__init__()
		self.alt = alt
		self.uris = uris


class UserBlock(Datablock):
	block_name = "user"
	def __init__(self,display_name:str,display_tier:str,display_icon_uri:str) -> None:
		super().__init__()
		self.display_name = display_name
		self.display_tier = display_tier
		self.display_icon_uri = display_icon_uri

class UnlockBalanceBlock(Datablock):
	block_name="unlock_balance"
	def __init__(self,balance:int,balance_unit:str,balance_refill_url:str) -> None:
		super().__init__()
		self.balance = balance
		self.balance_unit = balance_unit
		self.balance_refill_url = balance_refill_url

class UnlockLinkBlock(Datablock):
	block_name="unlock_link"
	def __init__(self,unlock_query_id:str,unlocked_datablocks_query:templates.FixedQuery):
		self.unlock_query_id = unlock_query_id
		self.unlocked_datablocks_query = unlocked_datablocks_query

def unlock_link_block_from_path(file_path:pathlib.Path) -> UnlockLinkBlock:
	return UnlockLinkBlock(file_path.parent.name,templates.FixedQuery(
		f"{config.API_URL}/unlocked_datablocks",
		templates.HttpMethod.GET,
		{
			"asset_id":file_path.parent.parent.name,
			"implementation_prefix":file_path.parent.name,
			"file_name":file_path.name
		}
	))

class UnlockQuery:
	def __init__(self,id:str,unlocked:bool,price:int,unlock_query:templates.FixedQuery,unlock_query_fallback_uri:str) -> None:
		self.id = id
		self.unlocked = unlocked
		self.price = price
		self.unlock_query = unlock_query
		self.unlock_query_fallback_uri = unlock_query_fallback_uri

class UnlockQueriesBlock(Datablock,List[UnlockQuery]):
	block_name = "unlock_queries"

def unlock_queries_block_from_directory(directory_path : pathlib.Path,user:users.AssetFetchUser) -> UnlockQueriesBlock:
	asset_id = directory_path.name
	subdirectories = list(pathlib.Path.iterdir())
	
	unlock_queries_block = UnlockQueriesBlock()

	for s in subdirectories:
		unlock_queries_block.append(
			UnlockQuery(
				id=s.name,
				unlocked= (f"{asset_id}/{s.name}" in user.get_all_purchased_identifiers()),
				price=1,
				unlock_query=templates.FixedQuery(f"{config.API_URL}/unlock",templates.HttpMethod.POST,{
					"asset_id":asset_id,
					"implementation_prefix":s.name
				})
			)
		)
	return unlock_queries_block
