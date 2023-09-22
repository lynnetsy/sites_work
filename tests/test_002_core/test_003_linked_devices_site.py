import asyncio
import pytest
import pytest
from loguru import logger
from device_inventory.models.coutry import Country
from device_inventory.models.device import Device
from device_inventory.models.device_properties import Site
from device_inventory.models.state import State
from device_inventory.models.municipality import Municipality
from device_inventory.models.city import City
from test.fixture import actions

@pytest.fixture
def tenant_info_fixture():
    return {
        # "header": "header_test_server",
        "hostname": "test-core-hostname"
    }

@pytest.fixture
def complete_site():
    return {
        "name": "Universidad Central",
        "latitud": -0.1807,
        "longitud": -78.4678,
        "address": "Av. Universitaria 123",
        "country": "Ecuador",
        "state": "Pichincha",
        "municipality": "Quito",
        "city": "La Carolina"
    }

@pytest.fixture
def complete_site_2():
    return {
        "name": "Hospital General",
        "latitud": 34.0522,
        "longitud": -118.2437,
        "address": "123 Main St",
        "country": "United States",
        "state": "California",
        "municipality": "Los Angeles",
        "city": "Downtown"
    }

@pytest.fixture
def devices_list():
    return [
        
        {
            "vendor": "MikroTik",
            "serial_number": "BDC456",
            "status": "ACTIVE"
        },
        {
            "vendor": "Ubiquiti",
            "serial_number": "JUI789",
            "status": "ACTIVE"
        },
        {
            "vendor": "Ruckus",
            "serial_number": "TFR012",
            "status": "DECOMMISSIONED"
        },
        {
            "vendor": "Avaya",
            "serial_number": "OKL345",
            "status": "ACTIVE"
        },
        {
            "vendor": "Palo Alto Networks",
            "serial_number": "PLM678",
            "status": "ACTIVE"
        },
        {
            "vendor": "Checkpoint",
            "serial_number": "UJK901",
            "status": "DECOMMISSIONED"
        },
        {
            "vendor": "HPE",
            "serial_number": "YHG234",
            "status": "DECOMMISSIONED"
        },
        {
            "vendor": "IBM",
            "serial_number": "CDE567",
            "status": "ACTIVE"
        },
        {
            "vendor": "F5 Networks",
            "serial_number": "VBN890",
            "status": "ACTIVE"
        },
        {
            "vendor": "SonicWall",
            "serial_number": "WRE012",
            "status": "ACTIVE"
        }
    ]

@pytest.fixture
def devices_list_2():
    return [
        {
            "vendor": "Cisco",
            "serial_number": "CSC123",
            "status": "ACTIVE"
        },
        {
            "vendor": "HP",
            "serial_number": "HPQ456",
            "status": "ACTIVE"
        },
        {
            "vendor": "Juniper",
            "serial_number": "JNP789",
            "status": "DECOMMISSIONED"
        },
        {
            "vendor": "Aruba",
            "serial_number": "ARB012",
            "status": "ACTIVE"
        },
        {
            "vendor": "Fortinet",
            "serial_number": "FTN345",
            "status": "ACTIVE"
        },
        {
            "vendor": "Dell",
            "serial_number": "DEL678",
            "status": "DECOMMISSIONED"
        },
        {
            "vendor": "Microsoft",
            "serial_number": "MSF901",
            "status": "DECOMMISSIONED"
        },
        {
            "vendor": "IBM",
            "serial_number": "IBM234",
            "status": "ACTIVE"
        },
        {
            "vendor": "Palo Alto Networks",
            "serial_number": "PAN567",
            "status": "ACTIVE"
        },
        {
            "vendor": "F5 Networks",
            "serial_number": "FFN890",
            "status": "ACTIVE"
        }
    ]

@pytest.mark.asyncio
async def test_add_devices(tenant_info_fixture, devices_list, complete_site, actions):
    # Create pydantic objects
    countrySchema = Country(name=complete_site["country"])
    stateSchema = State(name=complete_site["state"])
    munSchema = Municipality(name=complete_site["municipality"])
    citySchema = City(name=complete_site["city"])
    # Create country, city, state, municipality in the actions
    country = await actions.get_country(tenant_info_fixture, countrySchema.country_key)
    state = await actions.get_state(tenant_info_fixture, stateSchema.state_key)
    mun = await actions.get_municipality(tenant_info_fixture, munSchema.municipality_key)
    city = await actions.get_city(tenant_info_fixture, citySchema.city_key)
    if country is None:
        country = await actions.create_country(tenant_info_fixture, country=countrySchema, origin="test_link")
    if state is None:
        state = await actions.create_state(tenant_info_fixture, state=stateSchema, origin="test_link")
    if mun is None:
        mun = await actions.create_municipality(tenant_info_fixture, municipality=munSchema, origin="test_link")
    if city is None:
        city = await actions.create_city(tenant_info_fixture, city=citySchema, origin="test_link")
    siteSchema = Site(**complete_site)
    await actions.create_site(tenant_info_fixture, site=siteSchema, origin='test_link')
    devices = []
    for device in devices_list:
        deviceSchema = Device(**device)
        devices.append(deviceSchema)
        exist = await actions.get_device(tenant_info_fixture, deviceSchema.device_key)
        if exist is None:
            await actions.create_device(tenant_info_fixture, deviceSchema, "add_actions")
    resp = await actions.add_devices_to_site(tenant_info_fixture, site=siteSchema, devices=devices, origin='test_add')
    if resp:
        assert resp == True
    else:
        assert False

@pytest.mark.asyncio
async def test_remove_devices(actions, tenant_info_fixture, devices_list_2, complete_site_2):
    # Create multiples devices
    # Create pydantic obj-schemas
    countrySchema = Country(name=complete_site_2["country"])
    stateSchema = State(name=complete_site_2["state"])
    munSchema = Municipality(name=complete_site_2["municipality"])
    citySchema = City(name=complete_site_2["city"])
    # Search if country, state, mun, city exists
    country = await actions.get_country(tenant_info_fixture, country_key=countrySchema.country_key)
    state = await actions.get_state(tenant_info_fixture, state_key=stateSchema.state_key)
    mun = await actions.get_municipality(tenant_info_fixture, munSchema.municipality_key)
    city = await actions.get_city(tenant_info_fixture, citySchema.city_key)
    if country is None:
        await actions.create_country(tenant_info_fixture, country=countrySchema, origin="t_associate")
    if state is None:
        await actions.create_state(tenant_info_fixture, state=stateSchema, origin="t_associate")
    if mun is None:
        await actions.create_municipality(tenant_info_fixture, municipality=munSchema, origin="t_associate")
    if city is None:
        await actions.create_city(tenant_info_fixture, city=citySchema, origin="t_associate")
    # Create site
    siteSchema = Site(**complete_site_2)
    site = await actions.create_site(tenant_info_fixture, site=siteSchema, origin="test_link")
    if site:
        devices = []
        for device in devices_list_2:
            deviceSchema = Device(**device)
            exist = await actions.get_device(tenant_info_fixture, deviceSchema.device_key)
            if exist is None:
                await actions.create_device(tenant_info_fixture, deviceSchema, "add_actions")
            devices.append(deviceSchema)
        # First associate devices
        add = await actions.add_devices_to_site(tenant_info_fixture, site=siteSchema, devices=devices, origin="rmov_action")
        # Then remove  
        if add:  
            resp = await actions.remove_devices_from_site(tenant_info_fixture, site=siteSchema, devices=devices)
        if resp:
            assert resp == True
    else:
        assert resp == False