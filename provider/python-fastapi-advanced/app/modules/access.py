from enum import Enum
from fastapi import status
from hashlib import sha512

from . import exceptions,users,templates

def sha512_from_string(string:str) -> str:
	return sha512(string.encode('utf-8')).hexdigest()

class AssetFetchVerificationResult:
	def __init__(self,success:bool,user:users.AssetFetchUser) -> None:
		self.success = success
		self.user = user

def validate_access_token(access_token : str|None,endpoint_kind : templates.EndpointKind) -> AssetFetchVerificationResult:
	if access_token is None:
		raise exceptions.AssetFetchException(endpoint_kind=endpoint_kind,message="No access token set.",status_code=status.HTTP_401_UNAUTHORIZED)
	else:
		token_hash = sha512_from_string(access_token)
		for user in users.DEMO_USERS:
			if( token_hash == user.token_sha512 ):
				return AssetFetchVerificationResult(success=True,user=user,message="OK")
		raise exceptions.AssetFetchException(endpoint_kind=endpoint_kind,message="Could not find a user for this access token.",status_code=status.HTTP_403_FORBIDDEN)