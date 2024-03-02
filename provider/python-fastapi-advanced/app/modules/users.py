import random
import string
from typing import Dict

class AssetFetchUser:
	def __init__(self,name:str,balance:int = 10) -> None:
		"""This is a simple mock-up of a user with a unique access token.

		Args:
			name (str): The name of the user.
		"""
		self.name = name
		self.balance = balance
		self.token_sha512 = None

	def generate_new_random_token(self) -> str:
		from . import access
		new_token = ''.join(random.choices(string.ascii_uppercase + string.digits, k=32))
		self.token_sha512 = access.sha512_from_string(new_token)
		return new_token
	
DEMO_USERS : Dict[str,AssetFetchUser] = {}

def create_if_not_existing(username:str):
	if username not in DEMO_USERS.keys():
		DEMO_USERS[username] = AssetFetchUser(username)
