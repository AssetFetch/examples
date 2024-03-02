from typing import Annotated, List
from fastapi import FastAPI, Request,Response,status
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
	return {
		"meta": templates.MetaField(templates.EndpointKind.initialization),
		"data": datablocks.DataField(
			[
				datablocks.AssetListQueryBlock(uri=f"{config.API_URL}/asset_list",method=templates.HttpMethod.GET,parameters=[]),
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
	access.validate_access_token(access_token=access_token,endpoint_kind=templates.EndpointKind.connection_status)
	return{
		"meta":templates.MetaField(templates.EndpointKind.connection_status),
		"data":{}
	}

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

	# Read asset yaml files
	for asset_yaml_file in asset_yaml_files:
		asset_list.append(assets.Asset(asset_yaml=asset_yaml_file))

	return {
		"meta":templates.MetaField(templates.EndpointKind.asset_list),
		"data":datablocks.DataField([]),
		"assets":asset_list
	}

	

@app.get("/implementation_list/{asset_name}")
def endpoint_implementation_list(asset_name:str,request:Request,response:Response,resolution:int = None,lod:str = None,format:str = None):

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

		# Check for required parameters.
		# The models in this demo only come with JPG textures, which is why the texture_format parameter is not required here.

		if resolution == None:
			raise exceptions.AssetFetchException(templates.EndpointKind.implementation_list,"Parameter 'resolution' is not set.",status_code=status.HTTP_400_BAD_REQUEST)
		
		if lod == None:
			raise exceptions.AssetFetchException(templates.EndpointKind.implementation_list,"Parameter 'lod' is not set.",status_code=status.HTTP_400_BAD_REQUEST)

		asset_path = pathlib.Path(f"{config.ASSET_DIRECTORY}/{asset_name}/lod.{lod}_tex.{resolution}k/")
		print(f"Asset path is {asset_path}")
		
		obj_files = list(asset_path.glob("*.obj"))
		if len(list(obj_files)) > 0:

			# Implementation 1: OBJ with MTL
			obj_mtl_implementation = implementations.AssetImplementation("OBJ+MTL",components=[],data=[
				datablocks.TextBlock("OBJ with MTL file")
			])

			# Add OBJs to implementation
			for obj_path in obj_files:
				obj_path = pathlib.Path(obj_path)
				obj_component = implementations.AssetImplementationComponent(obj_path.name,[
					datablocks.ObjFormatBlock(datablocks.ObjUpAxis.PLUS_Y,True),
					datablocks.file_fetch_download_block_from_path(obj_path),
					datablocks.file_info_block_from_path(obj_path,obj_path.name,datablocks.BehaviorStyle.FILE_ACTIVE)
				])
				obj_mtl_implementation.components.append(obj_component)

			# Add MTLs to implementation
			mtl_files = list(asset_path.glob("*.mtl"))
			for mtl_path in mtl_files:
				mtl_path = pathlib.Path(mtl_path)
				mtl_component = implementations.AssetImplementationComponent(mtl_path.name,[
					datablocks.file_fetch_download_block_from_path(mtl_path),
					datablocks.file_info_block_from_path(mtl_path,mtl_path.name,datablocks.BehaviorStyle.FILE_PASSIVE)
				])
				obj_mtl_implementation.components.append(mtl_component)

			# Add JPGs, but without any explicit references (those are handled by the mtl files)
			jpg_files = list(asset_path.glob("*.jpg"))
			for jpg_path in jpg_files:
				jpg_path = pathlib.Path(jpg_path)

				map_component = implementations.AssetImplementationComponent(jpg_path.name,[
					datablocks.file_fetch_download_block_from_path(jpg_path),
					datablocks.file_info_block_from_path(jpg_path,jpg_path.name,datablocks.BehaviorStyle.FILE_PASSIVE)
				])
				obj_mtl_implementation.components.append(map_component)

			implementation_list.append(obj_mtl_implementation)

			# Implementation 2: OBJ with loose PBR maps
			
			obj_loose_material_implementation = implementations.AssetImplementation(id="OBJ+LOOSE_MAPS",components=[],data=[
				datablocks.TextBlock("OBJ with PBR maps")
			])

			# Add OBJs to implementation, but without MTLs
			for obj_path in obj_files:
				obj_path = pathlib.Path(obj_path)
				obj_component = implementations.AssetImplementationComponent(obj_path.name,[
					datablocks.ObjFormatBlock(datablocks.ObjUpAxis.PLUS_Y,False),
					datablocks.file_fetch_download_block_from_path(obj_path),
					datablocks.file_info_block_from_path(obj_path,obj_path.name,datablocks.BehaviorStyle.FILE_ACTIVE),
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
						datablocks.file_fetch_download_block_from_path(jpg_path),
						datablocks.LooseMaterialDefineBlock(asset_name,map,colorspace),
						datablocks.file_info_block_from_path(jpg_path,jpg_path.name,datablocks.BehaviorStyle.FILE_PASSIVE)
					])
					obj_loose_material_implementation.components.append(map_component)

			implementation_list.append(obj_loose_material_implementation)
			
		# Implementation 3: USD files
		
		usd_files = list(asset_path.glob("*.usd?"))
		if len(usd_files) > 0:
			
			usd_implementation = implementations.AssetImplementation("USD",components=[],data=[
				datablocks.TextBlock("OpenUSD")
			])

			for usd_path in usd_files:
				usd_path = pathlib.Path(usd_path)
				usd_component = implementations.AssetImplementationComponent(usd_path.name,[
					datablocks.file_fetch_download_block_from_path(usd_path),
					datablocks.file_info_block_from_path(usd_path,usd_path.name,datablocks.BehaviorStyle.FILE_ACTIVE)
				])
				usd_implementation.components.append(usd_component)
			
			# Add JPGs, but without any explicit references (those are handled by the mtl files)
			jpg_files = list(asset_path.glob("*.jpg"))
			for jpg_path in jpg_files:
				jpg_path = pathlib.Path(jpg_path)

				map_component = implementations.AssetImplementationComponent(jpg_path.name,[
					datablocks.file_fetch_download_block_from_path(jpg_path),
					datablocks.file_info_block_from_path(jpg_path,jpg_path.name,datablocks.BehaviorStyle.FILE_PASSIVE)
				])
				usd_implementation.components.append(map_component)

			implementation_list.append(usd_implementation)

	if about_asset['kind'] == "material":
		if resolution == None:
			raise exceptions.AssetFetchException(templates.EndpointKind.implementation_list,"Parameter 'resolution' is not set.",status_code=status.HTTP_400_BAD_REQUEST)
		
		if format == None:
			raise exceptions.AssetFetchException(templates.EndpointKind.implementation_list,"Parameter 'format' is not set.",status_code=status.HTTP_400_BAD_REQUEST)
		
		asset_path = pathlib.Path(f"{config.ASSET_DIRECTORY}/{asset_name}/format.{format}_res.{resolution}k/")
		print(f"Asset path is {asset_path}")

		map_files = list(asset_path.glob("*.[jp][pn][g]"))
		if len(map_files) > 0:

			# Implementation 1: Loose material
			
			mat_loose_material_implementation = implementations.AssetImplementation(id="LOOSE",components=[],data=[
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
						datablocks.file_fetch_download_block_from_path(map_path),
						datablocks.LooseMaterialDefineBlock(asset_name,map,colorspace),
						datablocks.file_info_block_from_path(map_path,map_path.name,datablocks.BehaviorStyle.FILE_ACTIVE)
					])
					mat_loose_material_implementation.components.append(map_component)

			implementation_list.append(mat_loose_material_implementation)

		# Implementation 2: USD
		usd_files = list(asset_path.glob("*.usd?"))
		if len(usd_files) > 0:
			
			usd_implementation = implementations.AssetImplementation("USD",components=[],data=[
				datablocks.TextBlock("OpenUSD")
			])

			for usd_path in usd_files:
				usd_path = pathlib.Path(usd_path)
				usd_component = implementations.AssetImplementationComponent(usd_path.name,[
					datablocks.file_fetch_download_block_from_path(usd_path),
					datablocks.file_info_block_from_path(usd_path,usd_path.name,datablocks.BehaviorStyle.FILE_ACTIVE)
				])
				usd_implementation.components.append(usd_component)

			for map_path in map_files:
				map_path = pathlib.Path(map_path)

				map_component = implementations.AssetImplementationComponent(map_path.name,[
					datablocks.file_fetch_download_block_from_path(map_path),
					datablocks.file_info_block_from_path(map_path,map_path.name,datablocks.BehaviorStyle.FILE_PASSIVE)
				])
				usd_implementation.components.append(map_component)

			implementation_list.append(usd_implementation)

		mtlx_files = list(asset_path.glob("*.mtlx"))
		if len(mtlx_files) > 0:
			mtlx_implementation = implementations.AssetImplementation("MTLX",components=[],data=[
				datablocks.TextBlock("MTLX Material")
			])

			for mtlx_path in mtlx_files:
				mtlx_path = pathlib.Path(mtlx_path)
				mtlx_component = implementations.AssetImplementationComponent(mtlx_path.name,[
					datablocks.file_fetch_download_block_from_path(mtlx_path),
					datablocks.file_info_block_from_path(mtlx_path,mtlx_path.name,datablocks.BehaviorStyle.FILE_ACTIVE)
				])
				mtlx_implementation.components.append(mtlx_component)

			for map_path in map_files:
				map_path = pathlib.Path(map_path)

				map_component = implementations.AssetImplementationComponent(map_path.name,[
					datablocks.file_fetch_download_block_from_path(map_path),
					datablocks.file_info_block_from_path(map_path,map_path.name,datablocks.BehaviorStyle.FILE_PASSIVE)
				])
				mtlx_implementation.components.append(map_component)

			implementation_list.append(mtlx_implementation)

	return {
		"meta":templates.MetaField(templates.EndpointKind.implementation_list),
		"data":datablocks.DataField([]),
		"implementations":implementation_list
	}