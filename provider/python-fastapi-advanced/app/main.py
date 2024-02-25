from typing import Annotated, List
from fastapi import FastAPI, HTTPException, Request,Response,status,Header
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import re,pathlib,yaml

from modules import *

# Initial application setup
app = FastAPI()
app.add_exception_handler(exceptions.AssetFetchException,exceptions.assetfetch_exception_handler)

#The static directory contains all the files that are hosted for download.
app.mount("/static", StaticFiles(directory=config.ASSET_DIRECTORY), name="assets")

# Init Endpoint
@app.get("/")
def endpoint_initialization():
	return jsonable_encoder({
		"meta": templates.MetaField(templates.EndpointKind.initialization),
		"data": datablocks.DataField(
			[
				datablocks.AssetListQueryBlock(uri=f"{config.API_URL}/asset_list",method=templates.HttpMethod.GET,parameters=[]),
				datablocks.TextBlock("Advanced Example Provider","This is a more advanced provider for AssetFetch."),
				datablocks.HeadersBlock([
					datablocks.SingularHeader("access-token",True,True,"Access Token","","")
				]),
				datablocks.UnlockInitializationBlock("Credits",True,"",templates.FixedQuery("",templates.HttpMethod.GET,{})),
				datablocks.WebReferencesBlock([
					datablocks.SingularWebReference(
						"AssetFetch Website",
						"https://assetfetch.org"
					)
				]),
				datablocks.BrandingBlock("abcdef","","",""),
				datablocks.LicenseBlock("","")
			]
		)
	})

# Asset List Endpoint
@app.get("/asset_list")
def endpoint_asset_list(request : Request):

	# Verify token
	access_token = request.headers.get('access-token')
	#access.validate_access_token(access_token=access_token,endpoint_kind=templates.EndpointKind.asset_list)
		
	# Parse the asset directory
	asset_list : List[assets.Asset] = []
	root_dir = pathlib.Path(config.ASSET_DIRECTORY)
	asset_yaml_files = root_dir.glob("*/asset.yaml")

	for asset_yaml_file in asset_yaml_files:
		asset_list.append(assets.Asset(asset_yaml=asset_yaml_file))

	return {
		"meta":templates.MetaField(templates.EndpointKind.asset_list),
		"data":datablocks.DataField(),
		"assets":asset_list
	}

@app.get("/implementation_list/{asset_name}")
def endpoint_implementation_list(asset_name:str,request:Request,response:Response,resolution:int,lod:str):

	# Verify token
	access_token = request.headers.get('access-token')
	#access.validate_access_token(access_token=access_token,endpoint_kind=templates.EndpointKind.implementation_list)

	# Input sanitization for ID strings.
	# This is specifically to ensure that the asset_name does not contain any relative references (like ../ )
	asset_name = re.sub("[^0-9A-Za-z_]","",asset_name)

	# Search the right file for the asset name
	asset_yaml = pathlib.Path(f"{config.ASSET_DIRECTORY}/{asset_name}/asset.yaml")

	# Get the data for the requested asset
	try:
		with open(asset_yaml, 'r') as file:
			about_asset = yaml.safe_load(file)
	except FileNotFoundError:
		raise exceptions.AssetFetchException(templates.EndpointKind.implementation_list,f"Could not find an asset with name '{asset_name}'.",status.HTTP_404_NOT_FOUND)

	# Start parsing
	implementation_list : List[implementations.AssetImplementation] = []

	print(f"Asset is of type {about_asset['kind']}")

	if about_asset['kind'] == "model":

		asset_path = pathlib.Path(f"{config.ASSET_DIRECTORY}/{asset_name}/lod.{lod}_tex.{resolution}k/")
		print(f"Asset path is {asset_path}")

		
		obj_files = list(asset_path.glob("*.obj"))
		if len(list(obj_files)) > 0:

			# Implementation 1: OBJ with MTL
			obj_mtl_implementation = implementations.AssetImplementation("OBJ+MTL",[],[])

			# Add OBJs to implementation
			for obj_path in obj_files:
				obj_path = pathlib.Path(obj_path)
				obj_component = implementations.AssetImplementationComponent(obj_path.name,[
					datablocks.ObjFormatBlock(datablocks.ObjUpAxis.PLUS_Y,True),
					datablocks.fetch_file_block_from_path(obj_path,obj_path.name),
					datablocks.BehaviorBlock(datablocks.BehaviorStyle.ACTIVE)
				])
				obj_mtl_implementation.components.append(obj_component)

			# Add MTLs to implementation
			mtl_files = list(asset_path.glob("*.mtl"))
			for mtl_path in mtl_files:
				mtl_path = pathlib.Path(mtl_path)
				mtl_component = implementations.AssetImplementationComponent(mtl_path.name,[
					datablocks.fetch_file_block_from_path(mtl_path,mtl_path.name),
					datablocks.BehaviorBlock(datablocks.BehaviorStyle.PASSIVE)
				])
				obj_mtl_implementation.components.append(mtl_component)

			# Add JPGs, but without any explicit references (those are handled by the mtl files)
			jpg_files = list(asset_path.glob("*.jpg"))
			for jpg_path in jpg_files:
				jpg_path = pathlib.Path(jpg_path)

				map_component = implementations.AssetImplementationComponent(jpg_path.name,[
					datablocks.fetch_file_block_from_path(jpg_path,jpg_path.name),
					datablocks.BehaviorBlock(datablocks.BehaviorStyle.PASSIVE)
				])
				obj_mtl_implementation.components.append(map_component)

			implementation_list.append(obj_mtl_implementation)

			# Implementation 2: OBJ with loose PBR maps
			
			obj_loose_material_implementation = implementations.AssetImplementation("OBJ+LOOSE_MAPS",[],[])

			# Add OBJs to implementation, but without MTLs
			for obj_path in obj_files:
				obj_path = pathlib.Path(obj_path)
				obj_component = implementations.AssetImplementationComponent(obj_path.name,[
					datablocks.ObjFormatBlock(datablocks.ObjUpAxis.PLUS_Y,False),
					datablocks.fetch_file_block_from_path(obj_path,obj_path.name),
					datablocks.BehaviorBlock(datablocks.BehaviorStyle.ACTIVE),
					datablocks.LooseMaterialApplyBlock(asset_name,None)
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
						datablocks.fetch_file_block_from_path(jpg_path,jpg_path.name),
						datablocks.LooseMaterialDefineBlock(asset_name,map,colorspace),
						datablocks.BehaviorBlock(datablocks.BehaviorStyle.PASSIVE)
					])
					obj_loose_material_implementation.components.append(map_component)

			implementation_list.append(obj_loose_material_implementation)
			
		# Option 3: USD files
		
		usd_files = list(asset_path.glob("*.usd?"))
		if len(usd_files) > 0:
			
			usd_implementation = implementations.AssetImplementation("USD",[],[])

			for usd_path in usd_files:
				usd_path = pathlib.Path(usd_path)
				usd_component = implementations.AssetImplementationComponent(usd_path.name,[
					datablocks.fetch_file_block_from_path(usd_path,usd_path.name),
					datablocks.BehaviorBlock(datablocks.BehaviorStyle.ACTIVE)
				])
				usd_implementation.components.append(usd_component)
			
			# Add JPGs, but without any explicit references (those are handled by the mtl files)
			jpg_files = list(asset_path.glob("*.jpg"))
			for jpg_path in jpg_files:
				jpg_path = pathlib.Path(jpg_path)

				map_component = implementations.AssetImplementationComponent(jpg_path.name,[
					datablocks.fetch_file_block_from_path(jpg_path,jpg_path.name),
					datablocks.BehaviorBlock(datablocks.BehaviorStyle.PASSIVE)
				])
				usd_implementation.components.append(map_component)

			implementation_list.append(usd_implementation)
			

	return {
		"meta":templates.MetaField(templates.EndpointKind.implementation_list),
		"data":datablocks.DataField([]),
		"implementations":implementation_list
	}