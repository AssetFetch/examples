# Read environment variables

import os


ASSET_DIRECTORY = os.environ['AF_ASSET_DIRECTORY']
if not ASSET_DIRECTORY:
	raise Exception("Missing model directory environment variable.")

API_URL = os.environ['AF_API_URL']
if not API_URL:
	raise Exception("Missing host url environment variable.")

SQLITE_PATH = os.environ['AF_DB_PATH']
if not SQLITE_PATH:
	raise Exception("Missing SQLITE_PATH variable.")