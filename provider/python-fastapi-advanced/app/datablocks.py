

from typing import List
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

### DATABLOCKS

class ImplementationListQueryBlock(query.VariableQuery,Datablock):
	block_name = "implementation_list_query"

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

class LicenseBlock:
	block_name = "license"
	def __init__(self,license_spdx : str,license_uri:str) -> None:
		self.license_spdx = license_spdx
		self.license_uri = license_uri