import random
import string
from typing import List

class AssetFetchUser:
	def __init__(self,name:str,) -> None:
		"""This is a simple mock-up of a user with a unique access token.

		Args:
			name (str): The name of the user.
		"""
		self.name = name
		self.token_sha512 = None

	def generate_new_random_token(self) -> str:
		import access
		new_token = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
		self.token_sha512 = access.sha512_from_string(new_token)
		return new_token
	
# Create four demo users
DEMO_USERS : List[AssetFetchUser] = []
for name in ["Alice","Bob","Charlie","Delilah"]:
	DEMO_USERS.append(AssetFetchUser(name))