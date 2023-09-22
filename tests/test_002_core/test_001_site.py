import pytest
import asyncio
from loguru import logger
from device_inventory.models.device_properties import Site
from test.fixture import actions
from device_inventory.models.city import City
from device_inventory.models.coutry import Country
from device_inventory.models.device import Device
from device_inventory.models.state import State
from device_inventory.models.municipality import Municipality


@pytest.fixture
def tenant_info_fixture():
    return {
        "header": None,
        "hostname": "test-core-hostname"
    }

@pytest.fixture
def one_site():
    return {
        "name": "m_core_site"
    }

@pytest.fixture
def to_delete_site():
    return {
        "name": "del_core_sit"
    }

@pytest.fixture
def complete_site():
    return {
        "name": "corecom_site",
        "latitud": 70.5,
        "longitud": 80.5,
        "address": "random street 80",
        "zip_code": "1400",
        "country": "Mexico",
        "state": "Ciudad de Mexico",
        "municipality": "Miguel Hidalgo",
        "city": "Anzures",
    }

@pytest.fixture
def data_site_3():
    return {
        "name": "core_site_3",
        "latitud": 70.5,
        "longitud": 80.5,
        "address": "random street 80",
        "zip_code": None,
        "country": None,
        "state": None,
        "municipality": None,
        "city": None,
    }

@pytest.fixture
def data_site_4():
    return {
        "name": "core_site_4",
        "latitud": 50.5,
        "longitud": 50.5,
        "address": "random street 66",
        "zip_code": None,
        "country": None,
        "state": None,
        "municipality": None,
        "city": None,
    }

@pytest.fixture
def edit_minimal_site():
    return {
        "name": "core_min_sit"
    }

@pytest.fixture
def new_minimal_site():
    return {
        "name": "core_min_sit",
        "latitud": 79.5,
        "longitud": 89.5,
        "address": "random street 100",
        "country": "Peru",
        "state": "Lima",
        "municipality": "Unknown",
        "city": "Lima",
    }

@pytest.fixture
def edit_complete_site():
    return {
        "name": "coredit_site",
        "latitud": 60,
        "longitud": 29.5,
        "address": "Edit Complete Street",
        "country": "Peru",
        "state": "Lima",
        "municipality": "Pucusana",
        "city": "Pucusana",
    }

@pytest.fixture
def new_complete_site():
    return {
        "name": "coredit_site",
        "latitud": 70.5,
        "longitud": 80.5,
        "address": "i changed ad",
        "country": "Mxn change",
        "state": "Ciudad de Mexico",
        "municipality": "Miguel Hidalgo",
        "city": "Anzures",
    }

@pytest.fixture
def get_site():
    return {
        "name": "get_core_tst",
        "latitud": 60.5,
        "longitud": 49.5,
        "address": "random street 100",
        "country": "Peru",
        "state": "Lima",
        "municipality": "Los olivos",
        "city": "Lima",
    }

@pytest.fixture
def multiple_sites():
    return [
        {
            "name": "Site 1",
            "latitud": 34.0522,
            "longitud": -118.2437,
            "address": "123 Main St",
            "zip_code": "90001",
            "country": "United States",
            "state": "California",
            "municipality": "Los Angeles",
            "city": "Downtown LA",
        },
        {
            "name": "Site 2",
            "latitud": 40.7128,
            "longitud": -74.0060,
            "address": "456 Elm St",
            "zip_code": "10001",
            "country": "United States",
            "state": "New York",
            "municipality": "New York City",
            "city": "Manhattan",
        },
        {
            "name": "Site 3",
            "latitud": 51.5074,
            "longitud": -0.1278,
            "address": "789 Park Ln",
            "zip_code": "SW1A 1AA",
            "country": "United Kingdom",
            "state": "England",
            "municipality": "London",
            "city": "Westminster",
        },
        {
            "name": "Site 4",
            "latitud": -33.8688,
            "longitud": 151.2093,
            "address": "987 Beach Rd",
            "zip_code": "2000",
            "country": "Australia",
            "state": "New South Wales",
            "municipality": "Sydney",
            "city": "Sydney",
        },
        {
            "name": "Site 5",
            "latitud": 35.6895,
            "longitud": 139.6917,
            "address": "456 Sakura St",
            "zip_code": "100-0001",
            "country": "Japan",
            "state": "Tokyo",
            "municipality": "Chiyoda",
            "city": "Tokyo",
        },
    ]

@pytest.fixture
def multiple_devices():
    return [
        {
            "vendor": "Apple",
            "serial_number": "LYNS123",
            "status": "ACTIVE"
        },
        {
            "vendor": "Lenovo",
            "serial_number": "LND3453",
            "status": "ACTIVE"
        },
        {
            "vendor": "HP",
            "serial_number": "HP9999",
            "status": "ACTIVE"
        },
        {
            "vendor": "Dell",
            "serial_number": "DELL6666",
            "status": "ACTIVE"
        },
        {
            "vendor": "Samsung",
            "serial_number": "SAM6655",
            "status": "DECOMMISSIONED"
        }
    ]

@pytest.fixture
def multiple_devices_2():
    return [
        {
            "vendor": "App",
            "serial_number": "LYNS123",
            "status": "ACTIVE"
        },
        {
            "vendor": "Leno",
            "serial_number": "LND3453",
            "status": "ACTIVE"
        },
        {
            "vendor": "HP2",
            "serial_number": "HP9999",
            "status": "ACTIVE"
        }]

@pytest.fixture
def multiple_devices_3():
    return [
        {
            "vendor": "Apk",
            "serial_number": "LMNS123",
            "status": "ACTIVE"
        },
        {
            "vendor": "Leok",
            "serial_number": "LND3485",
            "status": "ACTIVE"
        },
        {
            "vendor": "HP3",
            "serial_number": "HP9678",
            "status": "ACTIVE"
        }]

async def create_site_devices(actions, tenant_info_fixture: dict, data_site: str, multiple_devices: list[Device]):
    siteSchema = Site(**data_site)
    new_site = await actions.create_site(tenant_info=tenant_info_fixture, site=siteSchema, origin="test_web")
    output_keys = []
    output_devices = []
    for dev in multiple_devices:
        deviceSchema = Device(**dev)
        dev_ = await actions.create_device(tenant_info=tenant_info_fixture, device=deviceSchema, origin='test_web')   
        output_keys.append(dev_.device_key)
        output_devices.append(dev_)
    return new_site[0].site_key, output_keys, new_site[0], output_devices

@pytest.mark.asyncio
async def test_create_minimal_site(actions, one_site, tenant_info_fixture):
    siteSchema = Site(**one_site)
    output = await actions.create_site(tenant_info=tenant_info_fixture, site=siteSchema, origin='test_action')
    assert output[0].site_key is not None
    assert isinstance(output[0], Site)

@pytest.mark.asyncio
async def test_create_complete_site(actions, complete_site, tenant_info_fixture):
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
        country = await actions.create_country(tenant_info=tenant_info_fixture, country=countrySchema, origin="test_link")
    if state is None:
        state = await actions.create_state(tenant_info=tenant_info_fixture, state=stateSchema, origin="test_link")
    if mun is None:
        mun = await actions.create_municipality(tenant_info=tenant_info_fixture, municipality=munSchema, origin="test_link")
    if city is None:
        city = await actions.create_city(tenant_info=tenant_info_fixture, city=citySchema, origin="test_link")
    siteSchema = Site(**complete_site)
    output = await actions.create_site(tenant_info=tenant_info_fixture, site=siteSchema, origin='test_actions')
    assert output[0].site_key is not None
    assert output[0].name == complete_site['name']
    assert isinstance(output[0], Site)

@pytest.mark.asyncio
async def test_list_sites(actions, tenant_info_fixture, multiple_sites):
    output_sites = []
    # First we create multiple sites
    for element in multiple_sites:
        siteSchema = Site(**element)
        site_ = await actions.create_site(tenant_info_fixture, siteSchema, 'core_list')
        output_sites.append(site_)
    output = await actions.list_sites(tenant_info=tenant_info_fixture)
    assert output is not None
    assert output['records'] is not None

@pytest.mark.asyncio
async def test_get_site_wo_devices(actions, get_site, tenant_info_fixture):
    # Create site
    site = None
    devices = None
    siteSchema = Site(**get_site)
    new_site = await actions.create_site(tenant_info=tenant_info_fixture, site=siteSchema, origin='tedit_core')
    # Get site
    asyncio.sleep(1)
    site, devices = await actions.get_site(tenant_info=tenant_info_fixture, site_key=site[0].site_key)
    assert site is not None
    assert site.name == new_site.name

@pytest.mark.asyncio
async def test_delete_site(actions, to_delete_site, tenant_info_fixture):
    # Create Site
    Site_ = Site(**to_delete_site)
    new_site, devices = await actions.create_site(tenant_info=tenant_info_fixture, site=Site_, origin="edit_test")
    # Delete Site
    output = await actions.delete_site(tenant_info=tenant_info_fixture, site_key=new_site.site_key)
    assert output is True

@pytest.mark.asyncio
async def test_associate_devices(actions, multiple_devices_2, data_site_3, tenant_info_fixture):
    site_key, output_devices_keys, new_site, devices = await create_site_devices(actions, tenant_info_fixture, data_site_3, multiple_devices_2)
    associate = await actions.add_devices_to_site(tenant_info_fixture, new_site, devices, 'test_core')
    assert associate == True

@pytest.mark.asyncio
async def test_disassociate_devices(actions, multiple_devices_3, data_site_4, tenant_info_fixture):
    site_key, output_devices_keys, new_site, devices = await create_site_devices(actions, tenant_info_fixture, data_site_4, multiple_devices_3)
    associate = await actions.add_devices_to_site(tenant_info_fixture, new_site, devices, 'test_core')
    remove = await actions.remove_devices_from_site(tenant_info_fixture, new_site, devices)
    assert remove == True