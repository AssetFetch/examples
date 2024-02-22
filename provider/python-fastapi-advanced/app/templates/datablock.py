

from typing import List
from . import query


class Text:
	def __init__(self,title : str, description : str) -> None:
		self.title = title
		self.description = description

"""
An array of these headers forms the header datablock.
"""
class Headers_Header:
	def __init__(self,name : str, is_required : bool, is_sensitive: bool, title:str, acquisition_uri : str, acquisition_uri_title : str) -> None:
		self.name = name
		self.is_required = is_required
		self.is_sensitive = is_sensitive
		self.is_required = is_required
		self.title = title
		self.acquisistion_uri = acquisition_uri
		self.acquisistion_uri_title = acquisition_uri_title

class Headers(List[Headers_Header]):
	pass

class UnlockInitialization:
	def __init__(self,currency:str,is_prepaid:bool,prepaid_balance_refill_uri:str,prepaid_balance_check_query : query.AfFixedQuery) -> None:
		self.currency = currency
		self.is_prepaid = is_prepaid
		self.prepaid_balance_refill_uri = prepaid_balance_refill_uri

class WebReferences_WebReference:
	def __init__(self,title:str,uri:str) -> None:
		self.title = title
		self.uri = uri

class WebReferences(List[WebReferences_WebReference]):
	pass

class Branding:
	def __init__(self,color_accent:str,logo_square_uri:str,logo_wide_uri:str,banner_uri:str) -> None:
		self.color_accent = color_accent
		self.logo_square_uri = logo_square_uri
		self.logo_wide_uri = logo_wide_uri
		self.banner_uri = banner_uri

class License:
	def __init__(self,license_spdx : str,license_uri:str) -> None:
		self.license_spdx = license_spdx
		self.license_uri = license_uri