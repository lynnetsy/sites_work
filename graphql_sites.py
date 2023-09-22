import asyncio
from typing import Any
from graphql import GraphQLResolveInfo
from icecream import ic
from dependency_injector.wiring import inject, Provide
from fastapi import Depends
from loguru import logger

from device_inventory.adapters.web.graphql.query import query, mutation
from device_inventory.core.container import ActionsContainer
from device_inventory.core.actions import Actions
from device_inventory.models.device import Device
from device_inventory.models.device_properties import Site
from device_inventory.adapters.web.utils import tenant_info
from device_inventory.exceptions.db_implementatation import ItemAlreadyExist, ProcessingError, ItemDoesNotExist
from device_inventory.exceptions import TenantNotFound
from device_inventory.adapters.db.models.hubDevice import HubDevice


@query.field("sites")
@tenant_info
@inject
async def resolve_list_sites(
    obj: Any,
    info: GraphQLResolveInfo,
    # q,
    log: logger = Depends(Provide[ActionsContainer.logger]),
    actions: Actions = Depends(Provide[ActionsContainer.actions]),
    **data):
    log.bind(request_id='GraphQL').info("resolve_list_sites")

    tenant_info = info.context["tenant_info"]
    
    int(data["items"])
    success = False

    # Setup response
    edges = []
    success = False
    errors = []
    total_count = 0
    page_info = {
        "page_number": 0,
        "total_pages": 0,
        "has_previous_page": False,
        "has_next_page": False,
    }

    # Start list
    site_data = await actions.list_sites(tenant_info, **data)
    # If a problem occurs return empty data
    if(site_data is None):
        return {
            "success": success,
            "errors": errors,
            "total_count": total_count,
            "page_info": page_info,
            "edges": edges
        }

    success = True

    # Set page info
    page_info["page_number"] = site_data['page']
    page_info["total_pages"] = site_data['total_pages']
    page_info["has_previous_page"] = site_data['has_previous_page']
    page_info["has_next_page"] = site_data['has_next_page']
    total_count = site_data['total_records']

    for record in site_data['records']:
        devices = []
        device_response = []
        site = record['site']
        if 'devices' in record:
            devices = record['devices']
            for device in devices:
                device_formatted = {
                    'device_key': device.device_key,
                    'vendor': device.vendor,
                    'serial_number': device.serial_number, 
                    'hostname': device.hostname if device.hostname else None,
                    'description': device.description if device.description else None,
                    'status': device.status if device.status else None,
                    'cypher': device.cypher if device.cypher else None,
                    'host_key_algorithm': device.host_key_algorithm if device.host_key_algorithm else None,
                    'mac': device.mac if device.mac else None,
                    'device_type': device.device_type if device.device_type else None,
                    'tags': device.tags if device.tags else None,
                    'credentials': device.credentials if device.credentials else None,
                }
                device_response.append(device_formatted)
        edges.append({
            "cursor": site.site_key,
            "node": {
                "site_key": site.site_key,
                "name": site.name,
                "latitud": site.latitud if site.latitud else None,
                "longitud": site.longitud if site.longitud else None,
                "address": site.address if site.address else None,
                "country": site.country if site.country else None,
                "state": site.state if site.state else None,
                "municipality": site.municipality if site.municipality else None,
                "city": site.city if site.city else None,
                "devices": device_response,
            }
        })
    ic(edges)

    return {
        "success": success,
        "errors": errors,
        "total_count": total_count,
        "page_info": page_info,
        "edges": edges
    }

@query.field("site")
@tenant_info
@inject
async def resolve_get_site(
        obj: Any,
        info: GraphQLResolveInfo,
        site_key: str,
        log: logger = Depends(Provide[ActionsContainer.logger]),
        actions: Actions = Depends(Provide[ActionsContainer.actions]),
        **data,
        ):
    log.info("Site")

    # Setup the response
    success = False
    errors = []
    edge = {
            "cursor": '',
            "node": {}
    }
    try:
        # Search the data
        tenant_info = info.context['tenant_info']
        device_response = []
        devices = []
        site, devices = await actions.get_site(site_key=site_key, tenant_info=tenant_info)

        if site is None:
                errors = [f'Site {site_key} Not Found']
                return {
                    "success": success,
                    "errors": errors,
                    "edge": edge
                }

        else:
            if devices:
                for device in devices:
                    device_formatted = {
                        'device_key': device.device_key,
                        'vendor': device.vendor,
                        'serial_number': device.serial_number, 
                        'hostname': device.hostname if device.hostname else None,
                        'description': device.description if device.description else None,
                        'status': device.status if device.status else None,
                        'cypher': device.cypher if device.cypher else None,
                        'host_key_algorithm': device.host_key_algorithm if device.host_key_algorithm else None,
                        'mac': device.mac if device.mac else None,
                        'device_type': device.device_type if device.device_type else None,
                        'tags': device.tags if device.tags else None,
                        'credentials': device.credentials if device.credentials else None,
                    }
                    device_response.append(device_formatted)
            edge = {
                "cursor": site.site_key,
                "node": {
                    "site_key": site.site_key,
                    "name": site.name,
                    "latitud": site.latitud if site.latitud else None,
                    "longitud": site.longitud if site.longitud else None,
                    "address": site.address if site.address else None,
                    "country": site.country if site.country else None,
                    "state": site.state if site.state else None,
                    "municipality": site.municipality if site.municipality else None,
                    "city": site.city if site.city else None,
                    "devices": device_response if devices else [],
                }
            }
            return {
                "errors": errors,
                "edge": edge,
                "success": True
            }

    except Exception as e:
        errors = [f'Internal error getting site: {e}']
        ic(e)
        if isinstance(e, TenantNotFound):
            errors = ['Tenant Not Found']
        elif(isinstance(e, ValueError)):
            errors = [str(e)]
    

@mutation.field("create_site")
@tenant_info
@inject
async def resolve_create_site(
        obj: Any,
        info: GraphQLResolveInfo,
        log: logger = Depends(Provide[ActionsContainer.logger]),
        actions: Actions = Depends(Provide[ActionsContainer.actions]),
        **data):
    log.bind(request_id='GraphQL').info("resolve_edit_tenant")

    tenant_info = info.context["tenant_info"]

    # Setup the response data
    response = {
        "success": False,
        "error": [],
        "edge":
            {
                "cursor": None,
                "node": None
            }
    }

    try:
        siteSchema = Site(**data)
        new_site = await actions.create_site(tenant_info=tenant_info, site=siteSchema, origin=data['origin'])
        if new_site is not None:
            site_obj = new_site[0]
            cursor = site_obj.site_key
            response["edge"]["cursor"] = cursor
            node = {
                    "site_key": new_site[0].site_key if new_site[0] else None,
                    "name": new_site[0].name if new_site[0] else None,
                    "latitud": new_site[0].latitud if new_site[0].latitud else None, 
                    "longitud": new_site[0].longitud if new_site[0].longitud else None,
                    "address": new_site[0].address if new_site[0].address else None,
                    "zip_code": new_site[0].zip_code if new_site[0].zip_code else None,
                    "country": new_site[0].country if new_site[0].country else None,
                    "state": new_site[0].state if new_site[0].state else None,
                    "municipality": new_site[0].municipality if new_site[0].municipality else None,
                    "country": new_site[0].country if new_site[0].country else None,
                    "state": new_site[0].state if new_site[0].state else None,
                    "municipality": new_site[0].municipality if new_site[0].municipality else None,
                    "city": new_site[0].city if new_site[0].city else None,
                }
            response["edge"]["node"] = node
            response['success'] = True
    except Exception as e:
        log.error(e)
        success = False
        error = str(e)

    return response

# @mutation.field("edit_site")
# @tenant_info
# @inject
# async def resolve_edit_site(
    #     obj: Any,
    #     info: GraphQLResolveInfo,
    #     site_key: str,
    #     log: logger = Depends(Provide[ActionsContainer.logger]),
    #     actions: Actions = Depends(Provide[ActionsContainer.actions]),
    #     **data):
    # log.bind(request_id='GraphQL').info("resolve_edit_tenant")

    # tenant_info = info.context["tenant_info"]

    # success = False
    # n_site = Site(**data)

    # error = ""
    # try:
    #     res = await actions.edit_site(tenant_info=tenant_info, site_key=str(site_key), new_site=n_site)
    #     if res.id is not None:
    #         success = True
    #         cursor = res.site_key if res else None
    #         node = {
    #                 "site_key": res.site_key if res else None,
    #                 # "name": res.name if res.name else None,
    #                 "latitud": res.latitud if res.latitud else None, 
    #                 "longitud": res.longitud if res.longitud else None,
    #                 "address": res.address if res.address else None,
    #                 "country": res.country if res.country else None,
    #                 "state": res.state if res.state else None,
    #                 "municipality": res.municipality if res.municipality else None,
    #                 "city": res.city if res.city else None
    #             }
    # except Exception as e:
    #     log.error(e)
    #     success = False
    #     error = str(e)
    # return {
    #     "success": success,
    #     "errors": error,
    #     "edge":
    #         {
    #             "cursor": cursor,
    #             "node": node
    #         }
    # }

@mutation.field("delete_site")
@tenant_info
@inject
async def resolve_delete_site(
        obj: Any,
        info: GraphQLResolveInfo,
        site_key: str,
        log: logger = Depends(Provide[ActionsContainer.logger]),
        actions: Actions = Depends(Provide[ActionsContainer.actions])):
    log.bind(request_id='GraphQL').info("resolve_edit_tenant")

    tenant_info = info.context["tenant_info"]

    success = False
    errors = []
    try:
        res = await actions.delete_site(tenant_info=tenant_info, site_key=str(site_key))
        if res:
            success = True
    except Exception as e:
        log.error(e)
        success = False
        errors = [str(e)]
    return {
        "success": success,
        "errors": errors
    }

@mutation.field("associate_device_to_site")
@tenant_info
@inject
async def resolve_associate_device_to_site(
        obj: Any,
        info: GraphQLResolveInfo,
        log: logger = Depends(Provide[ActionsContainer.logger]),
        actions: Actions = Depends(Provide[ActionsContainer.actions]),
        **data):
        
    log.bind(request_id='GraphQL').info("resolve_associate_devices_to_site")

    tenant_info = info.context["tenant_info"]
    site_key = data['site_key']
    device_keys = data['devices']
    origin = data['origin']

    # Setup the response data
    response = {
        "success": False,
        "error": [],
        "edge":
            {
                "cursor": None,
                "node": None
            }
    }

    try:
        site = await actions.get_site(tenant_info=tenant_info, site_key=site_key)
        ic(site)
        if isinstance(site[0], Site):
            device_list = await actions.add_devices_to_site(tenant_info=tenant_info, site=site[0], keys=device_keys, origin=origin)
        # Validate the result of associate devices
        if(len(device_list) <= 1):
            response['errors'] = ['Error associating devices to site']
            return response
        await asyncio.sleep(1)
        site_obj = device_list[0]
        arr_devices = device_list[1]
        #  cursor es un la llave del site
        cursor = site_obj.site_key
        response["edge"]["cursor"] = cursor
        node = {
            'site_key': cursor,
            'name': site_obj.name,
            'latitud': site_obj.latitud,
            'longitud': site_obj.longitud,
            'address': site_obj.address,
            'zip_code': site_obj.zip_code,
            'country': site_obj.country,
            'state': site_obj.state,
            'municipality': site_obj.municipality,
            'city': site_obj.city,
            'devices': arr_devices,
        }
        response["edge"]["node"] = node
        ic(response)
        response['success'] = True

    except Exception as e:
        ic(e)
        response['errors'] = ['Internal Error associating devices to site']
        if isinstance(e, TenantNotFound):
            response['errors'] = ['Tenant Not Found']
        elif(isinstance(e, ValueError)):
            response['errors'] = [str(e)]
        elif(isinstance(e, ItemAlreadyExist)):
            response['errors'] = [str(e)]
        elif(isinstance(e, ItemDoesNotExist)):
            response['errors'] = [str(e)]

    return response

# TODO: Checar la respuesta del cursor que esta en null y no puede
# Ser null
@mutation.field("disassociate_device_from_site")
@tenant_info
@inject
async def resolve_disassociate_device_from_site(
        obj: Any,
        info: GraphQLResolveInfo,
        log: logger = Depends(Provide[ActionsContainer.logger]),
        actions: Actions = Depends(Provide[ActionsContainer.actions]),
        **data):
        
    log.bind(request_id='GraphQL').info("resolve_associate_devices_to_site")

    tenant_info = info.context["tenant_info"]
    site_key = data['site_key']
    device_keys = data['devices']

    # Setup the response data
    response = {
        "success": False,
        "errors": [],
        "edge":
            {
                "cursor": None,
                "node": None
            }
    }
    try:
        site = await actions.get_site(tenant_info=tenant_info, site_key=site_key)
        ic(site)
        if isinstance(site[0], Site):
            # First convert string keys to pydantic objects
            removed = await actions.remove_devices_from_site(tenant_info=tenant_info, site=site[0], keys=device_keys)
        # Validate the result of associate devices
        if removed is None:
            response['errors'] = ['Error disassociating devices to site']
            return response
        site_obj = removed[0]
        arr_devices = removed[1]
        #  cursor es un arreglo de llaves de los devices
        cursor = site_key
        response["edge"]["cursor"] = cursor
        node = {
                'site_key': site_obj.site_key,
                'name': site_obj.name,
                'latitud': site_obj.latitud,
                'longitud': site_obj.longitud,
                'address': site_obj.address,
                'zip_code': site_obj.zip_code,
                'country': site_obj.country,
                'state': site_obj.state,
                'municipality': site_obj.municipality,
                'city': site_obj.city,
                'devices': arr_devices,
            }
        response["edge"]["node"] = node
        response['success'] = True

    except Exception as e:
        ic(e)
        response['errors'] = [f'Internal Error disassociating devices to site: {str(e)}']
        if isinstance(e, TenantNotFound):
            response['errors'] = ['Tenant Not Found']
        elif(isinstance(e, ValueError)):
            response['errors'] = [str(e)]
        elif(isinstance(e, ItemAlreadyExist)):
            response['errors'] = [str(e)]
        elif(isinstance(e, ItemDoesNotExist)):
            response['errors'] = [str(e)]

    return response