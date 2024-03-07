import random, string, datetime
from typing import Dict,List

class AssetFetchPurchase:
	def __init__(self,purchase_identifier:str) -> None:
		self.purchase_identifier = purchase_identifier
		self.purchase_time = datetime.datetime.now()

class AssetFetchUser:
	def __init__(self,name:str,balance:int = 10) -> None:
		"""This is a simple mock-up of a user with a unique access token.

		Args:
			name (str): The name of the user.
		"""
		self.name = name
		self.balance = balance
		self.token_sha512 = None
		self.purchases : List[AssetFetchPurchase] = list()

	def get_owned_asset_names(self):
		output = []
		for i in self.owns_implementations:
			output.append(str.split(i,"/")[1])

	def generate_new_random_token(self) -> str:
		from . import access
		new_token = ''.join(random.choices(string.ascii_uppercase + string.digits, k=32))
		self.token_sha512 = access.sha512_from_string(new_token)
		return new_token
	
DEMO_USERS : Dict[str,AssetFetchUser] = {}

def create_if_not_existing(username:str):
	if username not in DEMO_USERS.keys():
		DEMO_USERS[username] = AssetFetchUser(username)
	
# Create user 'debug' with access-token 'debug'.
DEMO_USERS["debug"] = AssetFetchUser("debug",1000)
DEMO_USERS["debug"].token_sha512 = "225d05b918519458a8fcc1e6493a4e854c004da76f6250b8f52197f47094f71ee984725c31446a1967f0d55f4dc74793dd44d932f2bdf50d77d4288d663bf1ab"
