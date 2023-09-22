import pytest

from device_inventory.exceptions.db_implementatation import ItemAlreadyExist, ItemDoesNotExist
from device_inventory.models.coutry import Country
from device_inventory.models.device import Device
from device_inventory.models.device_properties import Site
from device_inventory.models.state import State
from device_inventory.models.municipality import Municipality
from device_inventory.models.city import City
from device_inventory.protocols.db import DBClientProtocol
from test.fixture import db

@pytest.fixture
def complete_site():
    return {
        "name": "Centro Comercial Paseo de la Rosa",
        "latitud": 19.4326,
        "longitud": -99.1332,
        "address": "Av. de la Rosa 123",
        "country": "México",
        "state": "Ciudad de México",
        "municipality": "Miguel Hidalgo",
        "city": "Polanco"
    }

@pytest.fixture
def complete_site_2():
    return {
        "name": "Shopping Mall Plaza Central",
        "latitud": 20.6735,
        "longitud": -103.3448,
        "address": "Av. Central 456",
        "country": "Mexico",
        "state": "Jalisco",
        "municipality": "Guadalajara",
        "city": "Zapopan"
    }

@pytest.fixture
def another_site():
    return {
        "site_key": "E7CC76799AE3A509FDCEA87DCAA861ED",
        "name": "complete_site",
    }

@pytest.fixture
def devices_list():
    return [
        {
            "vendor": "Cisco",
            "serial_number": "ABC123",
            "status": "ACTIVE"
        },
        {
            "vendor": "HP",
            "serial_number": "XYZ456",
            "status": "ACTIVE"
        },
        {
            "vendor": "Dell",
            "serial_number": "DEF789",
            "status": "ACTIVE"
        },
        {
            "vendor": "Juniper",
            "serial_number": "GHI012",
            "status": "ACTIVE"
        },
        {
            "vendor": "Huawei",
            "serial_number": "JKL345",
            "status": "DECOMMISSIONED"
        },
        {
            "vendor": "Aruba",
            "serial_number": "MNO678",
            "status": "DECOMMISSIONED"
        },
        {
            "vendor": "Fortinet",
            "serial_number": "PQR901",
            "status": "DECOMMISSIONED"
        },
        {
            "vendor": "Brocade",
            "serial_number": "STU234",
            "status": "DECOMMISSIONED"
        },
        {
            "vendor": "Extreme Networks",
            "serial_number": "VWX567",
            "status": "ACTIVE"
        },
        {
            "vendor": "Alcatel-Lucent",
            "serial_number": "YZA890",
            "status": "ACTIVE"
        }]

@pytest.fixture
def devices_list_2():
    return [
        {
            "vendor": "Microsoft",
            "serial_number": "MSFT123",
            "status": "ACTIVE"
        },
        {
            "vendor": "Apple",
            "serial_number": "APPL456",
            "status": "ACTIVE"
        },
        {
            "vendor": "Lenovo",
            "serial_number": "LENO789",
            "status": "ACTIVE"
        },
        {
            "vendor": "Sony",
            "serial_number": "SNY012",
            "status": "ACTIVE"
        },
        {
            "vendor": "Samsung",
            "serial_number": "SAM345",
            "status": "DECOMMISSIONED"
        },
        {
            "vendor": "LG",
            "serial_number": "LGE678",
            "status": "DECOMMISSIONED"
        },
        {
            "vendor": "ASUS",
            "serial_number": "ASUS901",
            "status": "DECOMMISSIONED"
        },
        {
            "vendor": "Acer",
            "serial_number": "ACR234",
            "status": "DECOMMISSIONED"
        },
        {
            "vendor": "HP",
            "serial_number": "HP567",
            "status": "ACTIVE"
        },
        {
            "vendor": "Dell",
            "serial_number": "DELL890",
            "status": "ACTIVE"
        }
    ]

@pytest.mark.asyncio
async def test_add_devices(db: DBClientProtocol, devices_list, complete_site):
    await db.init_client()
    # Create pydantic objects
    countrySchema = Country(name=complete_site["country"])
    stateSchema = State(name=complete_site["state"])
    munSchema = Municipality(name=complete_site["municipality"])
    citySchema = City(name=complete_site["city"])
    # Create country, city, state, municipality in the actions
    country = await db.get_country("test2", countrySchema.country_key)
    state = await db.get_state("test2", stateSchema.state_key)
    mun = await db.get_municipality("test2", munSchema.municipality_key)
    city = await db.get_city("test2", citySchema.city_key)
    if country is None:
        country = await db.create_country(tenant="test2", country=countrySchema, origin="test_link")
    if state is None:
        state = await db.create_state(tenant="test2", state=stateSchema, origin="test_link")
    if mun is None:
        mun = await db.create_municipality(tenant="test2", municipality=munSchema, origin="test_link")
    if city is None:
        city = await db.create_city(tenant="test2", city=citySchema, origin="test_link")
    siteSchema = Site(**complete_site)
    await db.create_site(tenant="test2", site=siteSchema, origin='test_link')
    devices = []
    for device in devices_list:
        deviceSchema = Device(**device)
        devices.append(deviceSchema)
        exist = await db.get_device("test2", deviceSchema.device_key)
        if exist is None:
            await db.create_device("test2", deviceSchema, "add_db")
    resp = await db.add_devices_to_site(tenant="test2", site=siteSchema, devices=devices, origin='test_add')
    assert resp == True

@pytest.mark.asyncio
async def test_remove_devices(db: DBClientProtocol, devices_list_2, complete_site_2):
    await db.init_client()
    # Create multiples devices
    # Create pydantic obj-schemas
    countrySchema = Country(name=complete_site_2["country"])
    stateSchema = State(name=complete_site_2["state"])
    munSchema = Municipality(name=complete_site_2["municipality"])
    citySchema = City(name=complete_site_2["city"])
    # Search if country, state, mun, city exists
    country = await db.get_country(tenant="test2", country_key=countrySchema.country_key)
    state = await db.get_state(tenant="test2", state_key=stateSchema.state_key)
    mun = await db.get_municipality("test2", munSchema.municipality_key)
    city = await db.get_city("test2", citySchema.city_key)
    if country is None:
        await db.create_country(tenant="test2", country=countrySchema, origin="t_associate")
    if state is None:
        await db.create_state(tenant="test2", state=stateSchema, origin="t_associate")
    if mun is None:
        await db.create_municipality(tenant="test2", municipality=munSchema, origin="t_associate")
    if city is None:
        await db.create_city(tenant="test2", city=citySchema, origin="t_associate")
    # Create site
    siteSchema = Site(**complete_site_2)
    site = await db.create_site(tenant="test2", site=siteSchema, origin="test_link")
    if site:
        devicesSchemas = []
        for device in devices_list_2:
            deviceSchema = Device(**device)
            devicesSchemas.append(deviceSchema)
            exist = await db.get_device("test2", deviceSchema.device_key)
            if exist is None:
                await db.create_device("test2", deviceSchema, "add_db")
        # First associate devices
        await db.add_devices_to_site(tenant="test2", site=siteSchema, devices=devicesSchemas, origin="remove_db")
        # Then remove    
        resp = await db.remove_devices_from_site(tenant='test2', site=siteSchema, devices=devicesSchemas)
        if resp:
            assert resp == True
    else:
        assert resp == False