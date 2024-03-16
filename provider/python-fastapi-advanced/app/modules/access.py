from enum import Enum
from fastapi import status
from hashlib import sha512

from . import exceptions,users,templates

def sha512_from_string(string:str) -> str:
	return sha512(string.encode('utf-8')).hexdigest()

def get_user_from_token(access_token : str|None,endpoint_kind : templates.EndpointKind) -> users.AssetFetchUser:
	if access_token is None:
		raise exceptions.AssetFetchException(endpoint_kind=endpoint_kind,message="No access token set.",status_code=status.HTTP_401_UNAUTHORIZED)
	else:
		token_hash = sha512_from_string(access_token)
		for username in users.DEMO_USERS.keys():
			if( token_hash == users.DEMO_USERS[username].token_sha512 ):
				return users.DEMO_USERS[username]
		raise exceptions.AssetFetchException(endpoint_kind=endpoint_kind,message="Could not find a user for this access token.",status_code=status.HTTP_403_FORBIDDEN)