from typing import List, Union, TypeVar, Type, Tuple
from loguru import logger
from icecream import ic
from device_inventory.models.tenant import Tenant as CoreTenant
from device_inventory.models.coutry import Country
from device_inventory.models.device import Device
from device_inventory.adapters.db.models.hubDevice import HubDevice
from device_inventory.models.state import State
from device_inventory.models.municipality import Municipality
from device_inventory.models.city import City
from device_inventory.protocols.db import DBClientProtocol
from device_inventory.models.tenant import Tenant as CoreTenant, TenantUpdate
from device_inventory.models.device_properties import Site
from device_inventory.exceptions import TenantNotFound
from math import ceil


class Actions:
    T = TypeVar('T')
    U = TypeVar('U')

    def __init__(self, db: DBClientProtocol, log: logger):
        self.db = db.db()
        self.logger = log

    async def init_client(self):
        await self.db.init_client()

    async def create_tenant(self, tenant: CoreTenant) -> CoreTenant:
        return await self.db.create_tenant(tenant)

    async def list_tenants(self, page: int = 0, items: int = -1, col_sort: list[str] = [], col_order: str = []) -> List[CoreTenant]:
        list_tenants = await self.db.list_tenants(page, items, col_sort, col_order)

        total_pages = ceil(list_tenants['total_records'] / items)
        if(items == -1): total_pages = 0

        has_previous_page = False
        if(page > 1): has_previous_page = True

        has_next_page = False
        if(total_pages > page):
            has_next_page = True

        return {
            'records' : list_tenants['records'],
            'total_records' : list_tenants['total_records'],
            'page' : page,
            'total_pages' : total_pages,
            'has_previous_page' : has_previous_page,
            'has_next_page' : has_next_page
        }

    async def get_tenant(self, tenant_id: str) -> CoreTenant:
        return await self.db.get_tenant(tenant_id)

    async def check_tenant(self, tenant_info: dict) -> Union[str, None]:
        exist_by_header = None
        if 'header' in tenant_info:
            exist_by_header = await self.db.get_tenant_schema(tenant_info['header'])

        exist_by_hostname = await self.db.get_tenant_schema(tenant_info['hostname'])

        # Tenant Not Found
        if exist_by_header is None and exist_by_hostname is None:
            return None

        # Find a tenant only by hostname
        if exist_by_header is None and exist_by_hostname is not None:
            return tenant_info['hostname']

        # Find a tenant only by header
        if exist_by_header is not None and exist_by_hostname is None:
            return tenant_info['header']

        # Find Tenant by both method but are different
        if exist_by_header != exist_by_hostname:
            return None

    async def get_tenant_by_name(self, tenant_name: str) -> CoreTenant:
        return await self.db.get_tenant_by_name(tenant_name)

    async def edit_tenant(self, tenant_id: str, new_tenant: TenantUpdate) -> CoreTenant:
        return await self.db.edit_tenant(tenant_id, new_tenant)
    
    async def delete_tenant(self, tenant_id: str) -> bool:
        return await self.db.delete_tenant(tenant_id)

    async def list_devices(self, tenant: str, page: int = 0, limit: int = -1) -> List[Device]:
        return await self.db.list_devices(tenant, page, limit)

    async def get_device(self, tenant_info: dict, device_key: str) -> Device:
        await self.init_client()
        check_tenant = await self.check_tenant(tenant_info)
        if check_tenant is not None:
            return await self.db.get_device(check_tenant, device_key)
        else:
            ic('no hay tenant')
            raise TenantNotFound
    
    async def create_device(self, tenant_info: dict, device: Device, origin: str) -> Device:
        await self.init_client()
        check_tenant = await self.check_tenant(tenant_info)
        if check_tenant is not None:
            return await self.db.create_device(check_tenant, device, origin)
        else:
            ic('no hay tenant')
            raise TenantNotFound
    
    async def create_site(self, tenant_info: dict, site: Site, origin: str) -> Site:
        await self.init_client()
        check_tenant = await self.check_tenant(tenant_info)
        if check_tenant is not None:
            return await self.db.create_site(check_tenant, site, origin)
        else:
            ic('no hay tenant')
            raise TenantNotFound
    
    async def get_site(self, tenant_info: dict, site_key: str) -> Site:
        await self.init_client()
        check_tenant = await self.check_tenant(tenant_info)
        ic(check_tenant)
        if check_tenant is not None:
            output = await self.db.get_site(check_tenant, site_key)
            return output
        return None
    
    async def edit_site(self, tenant_info: dict, site: Site, site_key: str,origin: str) -> Site:
        await self.init_client()
        check_tenant = await self.check_tenant(tenant_info)
        ic(check_tenant)
        if check_tenant is not None:
            return await self.db.edit_site(check_tenant, site, site_key, origin)
        return None

    async def list_sites(self, tenant_info: dict, page: int = 0, items: int = -1) -> List[Site]:
        await self.init_client()
        check_tenant = await self.check_tenant(tenant_info)
        if check_tenant is not None:
            list_sites = await self.db.list_sites(check_tenant, page, items)        
            total_pages = ceil(list_sites['total_records'] / items)
            if(items == -1): total_pages = 0

            has_previous_page = False
            if(page > 1): has_previous_page = True

            has_next_page = False
            if(total_pages > page):
                has_next_page = True
    
            return {
                'records' : list_sites['records'],
                'total_records' : list_sites['total_records'],
                'page' : page,
                'total_pages' : total_pages,
                'has_previous_page' : has_previous_page,
                'has_next_page' : has_next_page
            }
        return None

    async def delete_site(self, tenant_info: dict, site_key: str) -> None:
        await self.init_client()
        check_tenant = await self.check_tenant(tenant_info)
        ic(check_tenant)
        if check_tenant is not None:
            return await self.db.delete_site(check_tenant, site_key)
        return None

    async def add_devices_to_site(self, tenant_info: dict, site: Site, origin: str, keys: Type[List]) -> Tuple[Site, List[Device]]:
        await self.init_client()
        # Verify if the tenant exist before store the data
        check_tenant = await self.check_tenant(tenant_info)
        if check_tenant is not None:
            devices = await self.keys_to_models(check_tenant, keys, pydantic_model=Device, sqlalchemy_model=HubDevice, sqlalchemy_field='hub_device_key')
            res = await self.db.add_devices_to_site(check_tenant, site, devices, origin)
            if res:
                return await self.db.get_site(check_tenant, site.site_key)
        else:
            raise TenantNotFound
    
    async def remove_devices_from_site(self, tenant_info: dict, site: Site, keys: Type[List]) -> Tuple[Site, List[Device]]:
        await self.init_client()
        # Verify if the tenant exist before store the data
        check_tenant = await self.check_tenant(tenant_info)
        ic(check_tenant)
        if check_tenant is not None:
            devices = await self.keys_to_models(check_tenant, keys, pydantic_model=Device, sqlalchemy_model=HubDevice, sqlalchemy_field='hub_device_key')
            res = await self.db.remove_devices_from_site(check_tenant, site, devices)
            ic(res)
            if res:
                return await self.db.get_site(check_tenant, site.site_key)
        else:
            return None
    
    async def create_country(self, tenant_info: dict, country: Country, origin: str) -> Country:
        await self.init_client()
        check_tenant = await self.check_tenant(tenant_info)
        ic(check_tenant)
        if check_tenant is not None:
            return await self.db.create_country(check_tenant, country, origin)
        else:
            raise TenantNotFound

    async def get_country_by_name(self, tenant_info: dict, country_name: str) -> Country:
        await self.init_client()
        check_tenant = await self.check_tenant(tenant_info)
        ic(check_tenant)
        if check_tenant is not None:
            return await self.db.get_country_by_name(check_tenant, country_name)
        else:
            raise TenantNotFound

    async def get_country(self, tenant_info: dict, country_key: str) -> Country:
        await self.init_client()
        check_tenant = await self.check_tenant(tenant_info)
        ic(check_tenant)
        if check_tenant is not None:
            return await self.db.get_country(check_tenant, country_key)
        else:
            raise TenantNotFound

    async def create_state(self, tenant_info: dict, state: State, origin: str) -> State:
        await self.init_client()
        check_tenant = await self.check_tenant(tenant_info)
        ic(check_tenant)
        if check_tenant is not None:
            return await self.db.create_state(check_tenant, state, origin)
        else:
            raise TenantNotFound
    
    async def get_state_by_name(self, tenant_info: dict, state_name: str):
        await self.init_client()
        check_tenant = await self.check_tenant(tenant_info)
        ic(check_tenant)
        if check_tenant is not None:
            return await self.db.get_state_by_name(check_tenant, state_name)
        else:
            raise TenantNotFound
    
    async def get_state(self, tenant_info: dict, state_key: str) -> State:
        await self.init_client()
        check_tenant = await self.check_tenant(tenant_info)
        ic(check_tenant)
        if check_tenant is not None:
            return await self.db.get_state(check_tenant, state_key)
        else:
            raise TenantNotFound

    async def create_municipality(self, tenant_info: dict, municipality: Municipality, origin: str) -> Municipality:
        await self.init_client()
        check_tenant = await self.check_tenant(tenant_info)
        ic(check_tenant)
        if check_tenant is not None:
            return await self.db.create_municipality(check_tenant, municipality, origin)
        else:
            raise TenantNotFound

    async def get_municipality_by_name(self, tenant_info: dict, municipality_name: str) -> Municipality:
        await self.init_client()
        check_tenant = await self.check_tenant(tenant_info)
        ic(check_tenant)
        if check_tenant is not None:
            return await self.db.get_municipality_by_name(check_tenant, municipality_name)
        else:
            raise TenantNotFound
    
    async def get_municipality(self, tenant_info: dict, municipality_key: str) -> Municipality:
        await self.init_client()
        check_tenant = await self.check_tenant(tenant_info)
        ic(check_tenant)
        if check_tenant is not None:
            return await self.db.get_municipality(check_tenant, municipality_key)
        else:
            raise TenantNotFound
    
    async def create_city(self, tenant_info: dict, city: City, origin: str) -> City:
        await self.init_client()
        check_tenant = await self.check_tenant(tenant_info)
        ic(check_tenant)
        if check_tenant is not None:
            return await self.db.create_city(check_tenant, city, origin)
        else:
            raise TenantNotFound
    
    async def get_city_by_name(self, tenant_info: dict, city_name: str) -> City:
        await self.init_client()
        check_tenant = await self.check_tenant(tenant_info)
        ic(check_tenant)
        if check_tenant is not None:
            return await self.db.get_city_by_name(check_tenant, city_name)
        else:
            raise TenantNotFound
    
    async def get_city(self, tenant_info: dict, city_key: str) -> City:
        await self.init_client()
        check_tenant = await self.check_tenant(tenant_info)
        ic(check_tenant)
        if check_tenant is not None:
            return await self.db.get_municipality(check_tenant, city_key)
        else:
            raise TenantNotFound

    async def keys_to_models(self, check_tenant: str, keys: Type[List], pydantic_model: Type[T], sqlalchemy_model: Type[U], sqlalchemy_field: str) -> List[T]:
        await self.init_client()
        models = await self.db.keys_to_models(check_tenant, keys, pydantic_model, sqlalchemy_model, sqlalchemy_field)
        if models:
            return models
        else:
            return None