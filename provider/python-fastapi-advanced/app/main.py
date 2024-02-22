from typing import Annotated, List
from fastapi import FastAPI, HTTPException, Request,Response,status,Header
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import os,re,pathlib,glob

from .templates import meta,query,datablock
from . import access
from . import error

# Read environment variables

ASSET_DIRECTORY = os.environ['AF_ASSET_DIRECTORY']
if not ASSET_DIRECTORY:
	raise Exception("Missing model directory environment variable.")

API_URL = os.environ['AF_API_URL']
if not API_URL:
	raise Exception("Missing host url environment variable.")

SQLITE_PATH = os.environ['AF_DB_PATH']
if not SQLITE_PATH:
	raise Exception("Missing SQLITE_PATH variable.")

# Define endpoints

app = FastAPI()

"""
Handle exceptions
"""

app.add_exception_handler(error.AssetFetchException,error.assetfetch_exception_handler)

"""
The static directory contains all the files that are hosted for download.
"""
app.mount("/static", StaticFiles(directory=ASSET_DIRECTORY), name="assets")

"""
This is the implementation of the initialization endpoint.
This endpoint is the first point of contact between a client and this provider.
"""
@app.get("/")
def endpoint_initialization():

	return {
		"meta":meta.AfMetaData(),
		"data":{
			# This datablock tells the client where to go to get the asset list
			"asset_list_query":query.AfVariableQuery(uri=f"{API_URL}/asset_list",method=query.AfHttpMethod.GET,parameters=[]),
			# This datablock tells the client a display name and a description for this provider
			"text":datablock.Text("Advanced Example Provider","This is a more advanced provider for AssetFetch."),
			"headers": datablock.Headers([
				datablock.Headers_Header("access-token",True,True,"Access Token","","")
			]),
			"unlock_initialization":datablock.UnlockInitialization("Credits",True,"",query.AfFixedQuery("",query.AfHttpMethod.GET,{})),
			"web_references":datablock.WebReferences([
				datablock.WebReferences_WebReference(
					"AssetFetch Website",
					"https://assetfetch.org"
				)
			]),
			"branding":datablock.Branding("abcdef","","",""),
			"license":datablock.License("","")
		},
	}

@app.get("/asset_list")
def endpoint_asset_list(access_token: Annotated[str | None , Header()] = None):

	# Test for access token
	if(not access.verify_token(access_token=access_token)):
		raise error.AssetFetchException("asset_list","Could not validate access token.",status.HTTP_401_UNAUTHORIZED)

	# Parse the asset directory
	assets = []
	root_dir = pathlib.Path(ASSET_DIRECTORY)
	asset_dirs = root_dir.glob("*/*")
	asset_names : List[str] = []

	# Get the paths of all OBJ files
	obj_files = list(glob.glob(pathname="*.obj",root_dir=ASSET_DIRECTORY))
	assets = []

	for obj_path in obj_files:

		obj_path = pathlib.Path(obj_path)
		asset_name = obj_path.name.split(".")[0]

		asset = {
			"name":asset_name,
			"data":{
				# This is the query that the client has to call to find out how to actually download the asset
				"implementations_query":{
					"uri": f"{API_URL}/implementation_list/{asset_name}",
					"method":"GET",
					"parameters":{}
				},
				"preview_image_thumbnail":{
					"uris":{
						256: f"{API_URL}/static/{asset_name}.png"
					}
				},
				"text":{
					"title": f"low-poly {asset_name} model"
				}
			}
		}
		assets.append(asset)

	output = {
		"meta":{
			"kind": "asset_list",
			"message":"OK",
			"version":"0.1"
		},
		"data":{},
		"assets": assets
	}

	return output

@app.get("/implementation_list/{asset_name}")
def endpoint_implementation_list(asset_name:str,response:Response):

	# Input sanitization for ID strings.
	asset_name = re.sub("[^0-9A-Za-z]","",asset_name)

	# Search the right file for the asset name

	asset_file = pathlib.Path(f"{ASSET_DIRECTORY}/{asset_name}.obj")

	if asset_file.exists():
		output = {
			"meta":{
				"kind": "implementation_list",
				"message":"OK",
				"version":"0.1"
			},
			"data":{},
			# There is only one implementation with one file, so we just define it right here
			# In a more complex implementation this would be generated programmatically
			"implementations":[
				{
					"name":"obj-untextured",
					"data":{
						"text":{
							"title": "Wavefront OBJ (Untextured)"
						}
					},
					"components":[
						{
							"name":asset_file.name,
							"data":{
								"fetch.file":{
									"component_query":{
										"uri": f"{API_URL}/static/{asset_file.name}",
										"method": "GET",
										"payload": None
									},
									"local_path":asset_file.name,
									"length":asset_file.stat().st_size,
									"extension":asset_file.suffix
								},
								"obj":{
									"up_axis": "+y",
									"use_mtl": False
								}
							}
						}
					]
				}
			]
		}
	else:
		output = {
			"meta":{
				"kind": "implementation_list",
				"message":"The requested asset could not be found.",
				"version":"0.1"
			}
		}
		response.status_code = status.HTTP_404_NOT_FOUND
		
	return output