
from enum import Enum
from fastapi import HTTPException

class AssetFetchActionType(Enum):
	LIST_ASSETS = 1

class AssetFetchAction:
	def __init__(self,action_type : AssetFetchActionType,subject : any) -> None:
		self.action_type = action_type
		self.subject = subject

def verify_token(access_token : str|None,action : AssetFetchAction = None) -> bool:

	# If there is no action, we always allow it
	if action is None:
		return True
	
	# WIP, currently we only check if a token is present at all
	if access_token is None:
		return False
	else:
		return True