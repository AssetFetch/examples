from typing import Annotated, List
from fastapi import FastAPI, Request,Response,status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import re,pathlib,yaml

from modules import *

# Initial application setup
app = FastAPI()
app.add_exception_handler(exceptions.AssetFetchException,exceptions.assetfetch_exception_handler)

# File endpoint
@app.get("/asset_file/{asset_id}/{implementation_prefix}/{file_name}")
def endpoint_file(request:Request,asset_id:str,implementation_prefix:str,file_name:str):

	# Verify token
	access_token = request.headers.get('access-token')
	user = access.get_user_from_token(access_token=access_token,endpoint_kind=None)

	# Input sanitization for ID strings.
	# This is specifically to ensure that the asset_id does not contain any relative references (like ../ )
	asset_id = re.sub("[^0-9a-z_-]","",asset_id)
	implementation_prefix = re.sub("[^0-9a-z_-]","",implementation_prefix)
	file_name = re.sub("[^0-9a-z._-]","",file_name)

	if f"{asset_id}/{implementation_prefix}" in user.get_all_purchased_identifiers():
		return FileResponse(f"{config.ASSET_DIRECTORY}/{asset_id}/{implementation_prefix}/{file_name}")
	raise exceptions.AssetFetchException(None,"File not accessible.",status_code=status.HTTP_403_FORBIDDEN)

@app.get("/thumbnail/{asset_id}")
def endpoint_thumbnail(asset_id:str):
	return FileResponse(f"{config.ASSET_DIRECTORY}/{asset_id}/thumb.png")

# Init Endpoint
@app.get("/")
def endpoint_initialization():
	return {
		"meta": templates.MetaField(templates.EndpointKind.initialization),
		"id": "advanced.examples.assetfetch.org",
		"data": datablocks.DataField(
			[
				datablocks.AssetListQueryBlock(uri=f"{config.API_URL}/asset_list",method=templates.HttpMethod.GET,parameters=[
					templates.HttpParameter(
						type= templates.HttpParameterType.text,
						id="filter",
						title="Filter",
						default="",
						mandatory=False
					)
				]),
				datablocks.TextBlock("Advanced Example Provider","This is a more advanced provider for AssetFetch."),
				datablocks.ProviderConfigurationBlock(
					headers=[datablocks.SingularHeader("access-token",True,True,"Access Token","","")],
					connection_status_query=templates.FixedQuery(f"{config.API_URL}/status",templates.HttpMethod.GET,{})),
				datablocks.WebReferencesBlock([
					datablocks.SingularWebReference(
						"AssetFetch Website",
						"https://assetfetch.org"
					)
				]),
				datablocks.BrandingBlock("abcdef",f"{config.API_URL}/media/logo_square.png",f"{config.API_URL}/media/logo_wide.png",f"{config.API_URL}/media/banner.png"),
				datablocks.LicenseBlock("",""),
			]
		)
	}

@app.get("/status")
def endpoint_connection_status(request:Request):
	# Verify token
	access_token = request.headers.get('access-token')
	user = access.get_user_from_token(access_token=access_token,endpoint_kind=templates.EndpointKind.connection_status)
	return{
		"meta":templates.MetaField(templates.EndpointKind.connection_status),
		"data":datablocks.DataField([
			datablocks.UserBlock(user.name,"Standard User","https://placekitten.com/256/256"),
			datablocks.UnlockBalanceBlock(user.balance,"credits",f"{config.API_URL}/user/{user.name}/set_balance?balance=20")
			]
		)
	}

# Asset List Endpoint
@app.get("/asset_list")
def endpoint_asset_list(request : Request,filter:str = ""):

	# Verify token
	access_token = request.headers.get('access-token')
	access.get_user_from_token(access_token=access_token,endpoint_kind=templates.EndpointKind.asset_list)

	# Parse the asset directory
	asset_list : List[assets.Asset] = []
	root_dir = pathlib.Path(config.ASSET_DIRECTORY)
	asset_yaml_files = root_dir.glob("*/asset.yaml")

	# Build proper filter array
	if filter:
		filter = filter.split(",")
		for i in range(len(filter)):
			filter[i] = filter[i].strip()

	

	# Read asset yaml files
	for asset_yaml_file in asset_yaml_files:
		with open(asset_yaml_file, 'r') as file:
			about_asset = yaml.safe_load(file)
			asset = assets.Asset(
				id=pathlib.Path(asset_yaml_file).parent.name,
				title=about_asset['title'],
				description=about_asset['description'],
				license_spdx=about_asset['license_spdx'],
				author=about_asset['author'],
				author_uri=about_asset['author_uri'],
				kind=about_asset['kind']
			)

		if filter:
			if set(filter).issubset(set(about_asset['tags'])):
				asset_list.append(asset)
		else:
			asset_list.append(asset)

	return {
		"meta":templates.MetaField(templates.EndpointKind.asset_list),
		"data":datablocks.DataField([]),
		"assets":asset_list
	}

	

@app.get("/implementation_list/{asset_id}")
def endpoint_implementation_list(asset_id:str,request:Request,response:Response,resolution:int = None,lod:str = None,format:str = None):

	# Verify token
	access_token = request.headers.get('access-token')
	user = access.get_user_from_token(access_token=access_token,endpoint_kind=templates.EndpointKind.implementation_list)

	# Input sanitization for ID strings.
	# This is specifically to ensure that the asset_id does not contain any relative references (like ../ )
	asset_id = re.sub("[^0-9a-z_]","",asset_id)

	# Search the right file for the asset name
	asset_yaml = pathlib.Path(f"{config.ASSET_DIRECTORY}/{asset_id}/asset.yaml")

	# Get the data for the requested asset
	try:
		with open(asset_yaml, 'r') as file:
			about_asset = yaml.safe_load(file)
	except FileNotFoundError:
		raise exceptions.AssetFetchException(templates.EndpointKind.implementation_list,f"Could not find an asset with name '{asset_id}'.",status.HTTP_404_NOT_FOUND)

	# Start parsing
	implementation_list : List[implementations.AssetImplementation] = []
	unlock_queries_block : datablocks.UnlockQueriesBlock = datablocks.UnlockQueriesBlock()

	print(f"Asset is of type {about_asset['kind']}")

	if about_asset['kind'] == "model":

		# Check for required parameters.
		# The models in this demo only come with JPG textures, which is why the texture_format parameter is not required here.

		if resolution == None:
			raise exceptions.AssetFetchException(templates.EndpointKind.implementation_list,"Parameter 'resolution' is not set.",status_code=status.HTTP_400_BAD_REQUEST)
		
		if lod == None:
			raise exceptions.AssetFetchException(templates.EndpointKind.implementation_list,"Parameter 'lod' is not set.",status_code=status.HTTP_400_BAD_REQUEST)

		implementation_prefix = f"lod-{lod}_tex-{resolution}k"

		asset_path = pathlib.Path(f"{config.ASSET_DIRECTORY}/{asset_id}/{implementation_prefix}/")
		print(f"Asset path is {asset_path}")
		
		obj_files = list(asset_path.glob("*.obj"))
		if len(list(obj_files)) > 0:

			# Implementation 1: OBJ with MTL
			obj_mtl_implementation = implementations.AssetImplementation(f"{implementation_prefix}_obj+mtl",components=[],data=[
				datablocks.TextBlock("OBJ with MTL file")
			])

			# Add OBJs to implementation
			for obj_path in obj_files:
				obj_path = pathlib.Path(obj_path)
				obj_component = implementations.AssetImplementationComponent(obj_path.name,[
					datablocks.ObjFormatBlock(datablocks.ObjUpAxis.PLUS_Y,True),
					datablocks.unlock_link_block_from_path(obj_path),
					datablocks.file_info_block_from_path(obj_path,obj_path.name,datablocks.BehaviorStyle.FILE_ACTIVE)
				])
				obj_mtl_implementation.components.append(obj_component)

			# Add MTLs to implementation
			mtl_files = list(asset_path.glob("*.mtl"))
			for mtl_path in mtl_files:
				mtl_path = pathlib.Path(mtl_path)
				mtl_component = implementations.AssetImplementationComponent(mtl_path.name,[
					datablocks.unlock_link_block_from_path(mtl_path),
					datablocks.file_info_block_from_path(mtl_path,mtl_path.name,datablocks.BehaviorStyle.FILE_PASSIVE)
				])
				obj_mtl_implementation.components.append(mtl_component)

			# Add JPGs, but without any explicit references (those are handled by the mtl files)
			jpg_files = list(asset_path.glob("*.jpg"))
			for jpg_path in jpg_files:
				jpg_path = pathlib.Path(jpg_path)

				map_component = implementations.AssetImplementationComponent(jpg_path.name,[
					datablocks.unlock_link_block_from_path(jpg_path),
					datablocks.file_info_block_from_path(jpg_path,jpg_path.name,datablocks.BehaviorStyle.FILE_PASSIVE)
				])
				obj_mtl_implementation.components.append(map_component)

			implementation_list.append(obj_mtl_implementation)

			# Implementation 2: OBJ with loose PBR maps
			
			obj_loose_material_implementation = implementations.AssetImplementation(id=f"{implementation_prefix}_obj+loose_maps",components=[],data=[
				datablocks.TextBlock("OBJ with PBR maps")
			])

			# Add OBJs to implementation, but without MTLs
			for obj_path in obj_files:
				obj_path = pathlib.Path(obj_path)
				obj_component = implementations.AssetImplementationComponent(obj_path.name,[
					datablocks.ObjFormatBlock(datablocks.ObjUpAxis.PLUS_Y,False),
					datablocks.unlock_link_block_from_path(obj_path),
					datablocks.file_info_block_from_path(obj_path,obj_path.name,datablocks.BehaviorStyle.FILE_ACTIVE),
					datablocks.LooseMaterialApplyBlock([datablocks.LooseMaterialApplyElement(asset_id,None)])
				])
				obj_loose_material_implementation.components.append(obj_component)

			jpg_files = list(asset_path.glob("*.jpg"))
			for jpg_path in jpg_files:
				jpg_path = pathlib.Path(jpg_path)
				
				# Determine which PBR map this file is
				map = None
				if "_color" in jpg_path.name:
					map=datablocks.LooseMaterialMapName.albedo
					colorspace = datablocks.LooseMaterialColorSpace.SRGB
				if "_normal_gl" in jpg_path.name:
					map=datablocks.LooseMaterialMapName.normal_plus_y
					colorspace = datablocks.LooseMaterialColorSpace.LINEAR
				if "_normal_dx" in jpg_path.name:
					map=datablocks.LooseMaterialMapName.normal_minus_y
					colorspace = datablocks.LooseMaterialColorSpace.LINEAR
				if "_ao" in jpg_path.name:
					map=datablocks.LooseMaterialMapName.ambient_occlusion
					colorspace = datablocks.LooseMaterialColorSpace.LINEAR

				if map:
					map_component = implementations.AssetImplementationComponent(jpg_path.name,[
						datablocks.unlock_link_block_from_path(jpg_path),
						datablocks.LooseMaterialDefineBlock(asset_id,map,colorspace),
						datablocks.file_info_block_from_path(jpg_path,jpg_path.name,datablocks.BehaviorStyle.FILE_PASSIVE)
					])
					obj_loose_material_implementation.components.append(map_component)

			implementation_list.append(obj_loose_material_implementation)
			
		# Implementation 3: USD files
		
		usd_files = list(asset_path.glob("*.usd?"))
		if len(usd_files) > 0:
			
			usd_implementation = implementations.AssetImplementation(f"{implementation_prefix}_usd",components=[],data=[
				datablocks.TextBlock("OpenUSD")
			])

			for usd_path in usd_files:
				usd_path = pathlib.Path(usd_path)
				usd_component = implementations.AssetImplementationComponent(usd_path.name,[
					datablocks.unlock_link_block_from_path(usd_path),
					datablocks.file_info_block_from_path(usd_path,usd_path.name,datablocks.BehaviorStyle.FILE_ACTIVE)
				])
				usd_implementation.components.append(usd_component)
			
			# Add JPGs, but without any explicit references (those are handled by the mtl files)
			jpg_files = list(asset_path.glob("*.jpg"))
			for jpg_path in jpg_files:
				jpg_path = pathlib.Path(jpg_path)

				map_component = implementations.AssetImplementationComponent(jpg_path.name,[
					datablocks.unlock_link_block_from_path(jpg_path),
					datablocks.file_info_block_from_path(jpg_path,jpg_path.name,datablocks.BehaviorStyle.FILE_PASSIVE)
				])
				usd_implementation.components.append(map_component)

			implementation_list.append(usd_implementation)

	if about_asset['kind'] == "material":
		if resolution == None:
			raise exceptions.AssetFetchException(templates.EndpointKind.implementation_list,"Parameter 'resolution' is not set.",status_code=status.HTTP_400_BAD_REQUEST)
		
		if format == None:
			raise exceptions.AssetFetchException(templates.EndpointKind.implementation_list,"Parameter 'format' is not set.",status_code=status.HTTP_400_BAD_REQUEST)
		
		implementation_prefix = f"format-{format}_res-{resolution}k"

		asset_path = pathlib.Path(f"{config.ASSET_DIRECTORY}/{asset_id}/{implementation_prefix}/")
		print(f"Asset path is {asset_path}")

		map_files = list(asset_path.glob("*.[jp][pn][g]"))
		if len(map_files) > 0:

			# Implementation 1: Loose material
			
			mat_loose_material_implementation = implementations.AssetImplementation(id=f"{implementation_prefix}_loose",components=[],data=[
				datablocks.TextBlock("Set of PBR maps.")
			])

			for map_path in map_files:
				map_path = pathlib.Path(map_path)

				# Determine which PBR map this file is
				map = None
				if "_color" in map_path.name:
					map=datablocks.LooseMaterialMapName.albedo
					colorspace = datablocks.LooseMaterialColorSpace.SRGB
				if "_normal_gl" in map_path.name:
					map=datablocks.LooseMaterialMapName.normal_plus_y
					colorspace = datablocks.LooseMaterialColorSpace.LINEAR
				if "_normal_dx" in map_path.name:
					map=datablocks.LooseMaterialMapName.normal_minus_y
					colorspace = datablocks.LooseMaterialColorSpace.LINEAR
				if "_ao" in map_path.name:
					map=datablocks.LooseMaterialMapName.ambient_occlusion
					colorspace = datablocks.LooseMaterialColorSpace.LINEAR
				if "_roughness" in map_path.name:
					map=datablocks.LooseMaterialMapName.roughness
					colorspace = datablocks.LooseMaterialColorSpace.LINEAR
				if "_height" in map_path.name:
					map=datablocks.LooseMaterialMapName.height
					colorspace = datablocks.LooseMaterialColorSpace.LINEAR

				if map:
					map_component = implementations.AssetImplementationComponent(map_path.name,[
						datablocks.unlock_link_block_from_path(map_path),
						datablocks.LooseMaterialDefineBlock(asset_id,map,colorspace),
						datablocks.file_info_block_from_path(map_path,map_path.name,datablocks.BehaviorStyle.FILE_ACTIVE)
					])
					mat_loose_material_implementation.components.append(map_component)

			implementation_list.append(mat_loose_material_implementation)

		# Implementation 2: USD
		usd_files = list(asset_path.glob("*.usd?"))
		if len(usd_files) > 0:
			
			usd_implementation = implementations.AssetImplementation(f"{implementation_prefix}_usd",components=[],data=[
				datablocks.TextBlock("OpenUSD")
			])

			for usd_path in usd_files:
				usd_path = pathlib.Path(usd_path)
				usd_component = implementations.AssetImplementationComponent(usd_path.name,[
					datablocks.unlock_link_block_from_path(usd_path),
					datablocks.file_info_block_from_path(usd_path,usd_path.name,datablocks.BehaviorStyle.FILE_ACTIVE)
				])
				usd_implementation.components.append(usd_component)

			for map_path in map_files:
				map_path = pathlib.Path(map_path)

				map_component = implementations.AssetImplementationComponent(map_path.name,[
					datablocks.unlock_link_block_from_path(map_path),
					datablocks.file_info_block_from_path(map_path,map_path.name,datablocks.BehaviorStyle.FILE_PASSIVE)
				])
				usd_implementation.components.append(map_component)

			implementation_list.append(usd_implementation)

		mtlx_files = list(asset_path.glob("*.mtlx"))
		if len(mtlx_files) > 0:
			mtlx_implementation = implementations.AssetImplementation(f"{implementation_prefix}_mtlx",components=[],data=[
				datablocks.TextBlock("MTLX Material")
			])

			for mtlx_path in mtlx_files:
				mtlx_path = pathlib.Path(mtlx_path)
				mtlx_component = implementations.AssetImplementationComponent(mtlx_path.name,[
					datablocks.unlock_link_block_from_path(mtlx_path),
					datablocks.file_info_block_from_path(mtlx_path,mtlx_path.name,datablocks.BehaviorStyle.FILE_ACTIVE)
				])
				mtlx_implementation.components.append(mtlx_component)

			for map_path in map_files:
				map_path = pathlib.Path(map_path)

				map_component = implementations.AssetImplementationComponent(map_path.name,[
					datablocks.unlock_link_block_from_path(map_path),
					datablocks.file_info_block_from_path(map_path,map_path.name,datablocks.BehaviorStyle.FILE_PASSIVE)
				])
				mtlx_implementation.components.append(map_component)

			implementation_list.append(mtlx_implementation)

	# Test if the user already owns this implementation and generate unlock query accordingly
	unlock_queries_block.append(datablocks.UnlockQuery(
		id=implementation_prefix,
		unlocked= (f"{asset_id}/{implementation_prefix}" in user.get_all_purchased_identifiers()),
		price=1,
		unlock_query=templates.FixedQuery(
			f"{config.API_URL}/unlock",
			templates.HttpMethod.POST,
			{
				"asset_id":asset_id,
				"implementation_prefix":implementation_prefix
			}
		),
		unlock_query_fallback_uri=None
	))

	return {
		"meta":templates.MetaField(templates.EndpointKind.implementation_list),
		"data":datablocks.DataField([unlock_queries_block]),
		"implementations":implementation_list
	}

@app.post("/unlock")
def endpoint_unlock(request:Request,asset_id:str,implementation_prefix:str):
	
	# Verify token
	access_token = request.headers.get('access-token')
	user = access.get_user_from_token(access_token=access_token,endpoint_kind=templates.EndpointKind.asset_list)

	# Input sanitization for ID strings.
	# This is specifically to ensure that the asset_id does not contain any relative references (like ../ )
	asset_id = re.sub("[^0-9a-z_-]","",asset_id)
	implementation_prefix = re.sub("[^0-9a-z_-]","",implementation_prefix)

	# Verify that this implementation exists
	if implementation_prefix=="" or not pathlib.Path(f"{config.ASSET_DIRECTORY}/{asset_id}/{implementation_prefix}/").exists():
		raise exceptions.AssetFetchException(templates.EndpointKind.unlock,"This combination of asset/implementation does not exist.",status.HTTP_404_NOT_FOUND)

	if user.balance < 1:
		raise exceptions.AssetFetchException(templates.EndpointKind.unlock,"No implementation credits left.",status.HTTP_402_PAYMENT_REQUIRED)
	
	purchase_identifier = f"{asset_id}/{implementation_prefix}"
	if purchase_identifier not in user.get_all_purchased_identifiers():
		user.balance -= 1
		user.purchases.append(users.AssetFetchPurchase(purchase_identifier=purchase_identifier))

	return{
		"meta":templates.MetaField(templates.EndpointKind.unlock)
	}

@app.get("/unlocked_datablocks")
def endpoint_unlocked_datablocks(request:Request,asset_id:str,implementation_prefix:str,file_name:str):

	# Verify token
	access_token = request.headers.get('access-token')
	user = access.get_user_from_token(access_token=access_token,endpoint_kind=templates.EndpointKind.asset_list)

	# Input sanitization for ID strings.
	# This is specifically to ensure that the asset_id does not contain any relative references (like ../ )
	asset_id = re.sub("[^0-9a-z_-]","",asset_id)
	implementation_prefix = re.sub("[^0-9a-z_-]","",implementation_prefix)
	file_name = re.sub("[^0-9a-z._-]","",file_name)

	for p in user.purchases:
		if p.purchase_identifier == f"{asset_id}/{implementation_prefix}":
			return{
				"meta":templates.MetaField(templates.EndpointKind.unlocked_datablocks),
				"data":datablocks.DataField([
					datablocks.file_fetch_download_block_from_path(pathlib.Path(f"{config.ASSET_DIRECTORY}/{asset_id}/{implementation_prefix}/{file_name}"))
				])
			}
	raise exceptions.AssetFetchException(templates.EndpointKind.unlocked_datablocks,"The requested data was not found among this user's purchases.",status.HTTP_403_FORBIDDEN)


@app.get("/user/{user}/get_token")
def endpoint_get_token(user:str):
	users.create_if_not_existing(username=user)
	return {
		"user":user,
		"new_token": users.DEMO_USERS[user].generate_new_random_token()
	}

@app.get("/user/{user}/set_balance")
def endpoint_set_balance(balance:int,user:str):
	users.create_if_not_existing(username=user)
	users.DEMO_USERS[user].balance = balance
	return{
		"user":user,
		"new_balance": users.DEMO_USERS[user].balance
	}

@app.get("/users")
def endpoint_users():
	return users.DEMO_USERS