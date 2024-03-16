# Read environment variables

import os


if os.environ.get("AF_ASSET_DIRECTORY") is not None:
	ASSET_DIRECTORY = os.environ.get("AF_ASSET_DIRECTORY")
else:
	raise Exception("Missing asset directory environment variable.")


if os.environ.get("AF_API_URL") is not None:
	API_URL = os.environ['AF_API_URL']
else:
	raise Exception("Missing host url environment variable.")

