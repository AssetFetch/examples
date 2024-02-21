from fastapi import FastAPI,Response,status
from fastapi.staticfiles import StaticFiles
import os,re,pathlib,glob

# Read environment variables

MODEL_DIRECTORY = os.environ['AF_MODEL_DIRECTORY']
if not MODEL_DIRECTORY:
	raise Exception("Missing model directory environment variable.")

API_URL = os.environ['AF_API_URL']
if not API_URL:
	raise Exception("Missing host url environment variable.")

# Define endpoints

app = FastAPI()

"""
The static directory contains all the files that are hosted for download.
"""
app.mount("/static", StaticFiles(directory=MODEL_DIRECTORY), name="assets")

"""
This is the implementation of the initialization endpoint.
This endpoint is the first point of contact between a client and this provider.
"""
@app.get("/")
def endpoint_initialization():

	output = {
		"meta":{
			"kind": "initialization",
			"message":"OK",
			"version":"0.1"
		},
		"data":{
			# This datablock tells the client where to go to get the asset list
			"asset_list_query":{
				"uri": f"{API_URL}/asset_list",
				"method":"GET",
				"parameters":{}
			},
			# This datablock tells the client a display name and a description for this provider
			"text":{
				"title": "Minimal AssetFetch Implementation",
				"description": "This is a bare-bones sample implementation of an AssetFetch provider."
			},
			"headers": [
				{
					"name":"af-token",
					"is_required":True,
					"is_sensitive":True,
					"title":"Login token",
					"acquisition_uri":"",
					"acquisition_uri_title":""
				}
			],
			"unlock_initialization":{
				"currency": "Credits",
				"is_prepaid": true,
				"prepaid_balance_refill_uri":"",
				"prepaid_balance_check_query":{
					"uri":"",
					"method":"GET",
					"payload":{}
				}
			},
			"web_references":[
				{
					"title": "AssetFetch Website",
					"uri": "https://assetfetch.org"
				}
			],
			"branding":{
				"color_accent":"",
				"logo_square_uri":"",
				"logo_wide_uri":"",
				"banner_uri":""
			},
			"license":{
				"license_spdx":"",
				"license_uri":""
			}
		},
	}

	return output

@app.get("/asset_list")
def endpoint_asset_list():

	# Get the paths of all OBJ files
	obj_files = list(glob.glob(pathname="*.obj",root_dir=MODEL_DIRECTORY))
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

	asset_file = pathlib.Path(f"{MODEL_DIRECTORY}/{asset_name}.obj")

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