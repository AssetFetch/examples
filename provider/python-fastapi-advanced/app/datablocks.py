

from enum import Enum
from typing import Dict, List
from . import query
from abc import ABC,abstractmethod

class Datablock:
	"""Abstract class that all datablocks must implement.
	It ensures that every datablock has a block_name property
	"""
	@property
	@abstractmethod
	def block_name(self):
		pass

class DatablockContainer(Dict[str,Datablock]):
	def __init__(self,blocks : List[Datablock] | None) -> None:
		for b in blocks:
			self.set_block(b)

	def set_block(self,block:Datablock):
		self[block.block_name] = block

### DATABLOCKS

class ImplementationListQueryBlock(query.VariableQuery,Datablock):
	block_name = "implementation_list_query"

class AssetListQueryBlock(query.VariableQuery,Datablock):
	block_name = "asset_list_query"

class TextBlock(Datablock):
	block_name = "text"
	def __init__(self,title : str, description : str) -> None:
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
class HeadersBlock(List[SingularHeader],Datablock):
	block_name = "headers"

class UnlockInitializationBlock(Datablock):
	block_name = "unlock_initialization"
	def __init__(self,currency:str,is_prepaid:bool,prepaid_balance_refill_uri:str,prepaid_balance_check_query : query.FixedQuery) -> None:
		self.currency = currency
		self.is_prepaid = is_prepaid
		self.prepaid_balance_refill_uri = prepaid_balance_refill_uri

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

class BehaviorStyle(Enum):
	ACTIVE="active"
	PASSIVE="passive"

class BehaviorBlock(Datablock):
	block_name="behavior"
	def __init__(self,style:BehaviorStyle) -> None:
		super().__init__()
		self.style=style