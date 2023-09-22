import pytest

from device_inventory.exceptions.db_implementatation import ItemAlreadyExist, ItemDoesNotExist
from device_inventory.models.coutry import Country
from device_inventory.models.device import Device
from device_inventory.models.enums import DeviceStatus
from device_inventory.models.device_properties import Site
from device_inventory.models.state import State
from device_inventory.models.municipality import Municipality
from device_inventory.models.city import City
from device_inventory.protocols.db import DBClientProtocol
from test.fixture import db

@pytest.fixture
def one_site():
    return {
        "name": "minimal_site"
    }

@pytest.fixture
def one_device(complete_site):
    return {
        "vendor": "cisco",
        "serial_number": "123456",
        "status": DeviceStatus.ACTIVE,
        "hostname": "www.hola.com",
        "description": "test_site",
        "site": complete_site
    }

@pytest.fixture
def to_delete_site():
    return {
        "name": "deleted_site",
        "latitud": 70.5,
        "longitud": 80.5,
        "address": "random street 80",
        "country": "Mexico",
    }

@pytest.fixture
def complete_site():
    return {
        "name": "complete_site_db",
        "latitud": 70.5,
        "longitud": 80.5,
        "address": "random street 80",
        "zip_code": "11405",
        "country": "mexico",
        "state": "ciudad de mexico",
        "municipality": "miguel hidalgo",
        "city": "city-one",
    }

@pytest.fixture
def edit_minimal_site():
    return {
        "name": "edit_min_sit"
    }

@pytest.fixture
def new_minimal_site():
    return {
        "name": "edit_min_sit",
        "latitud": 79.5,
        "longitud": 89.5,
        "address": "random street 100",
        "zip_code": "11405",
        "country": "Peru",
        "state": "Lima",
        "municipality": "Unknown",
        "city": "Lima",
    }

@pytest.fixture
def edit_complete_site():
    return {
        "name": "c_edit_site",
        "latitud": 60,
        "longitud": 29.5,
        "address": "Edit Complete Street",
        "zip_code": "11405",
        "country": "Salai",
        "state": "Limon",
        "municipality": "Unknown",
        "city": "Limoncito",
    }

@pytest.fixture
def new_complete_site():
    return {
        "name": "c_edit_site",
        "latitud": 70.5,
        "longitud": 80.5,
        "address": "i changed ad",
        "zip_code": "11405",
        "country": "Mxn change",
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
def get_site():
    return {
        "name": "get_test",
        "latitud": 60.5,
        "longitud": 49.5,
        "address": "random street 100",
        "zip_code": "11405",
    }

@pytest.fixture
def multiple_sites():
    return [
    {
        "name": "Centro Comercial Paseo de la Rosa",
        "latitud": 19.4326,
        "longitud": -99.1332,
        "address": "Av. de la Rosa 123",
        "zip_code": "11405",
        "country": "México",
        "state": "Ciudad de México",
        "municipality": "Miguel Hidalgo",
        "city": "Polanco"
    },
    {
        "name": "Hotel Continental",
        "latitud": 20.6762,
        "longitud": -103.3467,
        "address": "Av. Juárez 456",
        "zip_code": "11405",
        "country": "México",
        "state": "Jalisco",
        "municipality": "Guadalajara",
        "city": "Centro"
    },
    {
        "name": "Parque del Bosque",
        "latitud": 25.6664,
        "longitud": -100.3096,
        "address": "Calle del Bosque 789",
        "zip_code": "11405",
        "country": "México",
        "state": "Nuevo León",
        "municipality": "San Pedro Garza García",
        "city": "Del Valle"
    },
    {
        "name": "Universidad del Sol",
        "latitud": 21.1606,
        "longitud": -86.8475,
        "address": "Av. del Sol 321",
        "zip_code": "11405",
        "country": "México",
        "state": "Quintana Roo",
        "municipality": "Cancún",
        "city": "Zona Hotelera"
    },
    {
        "name": "Residencial Montecarlo",
        "latitud": 25.6489,
        "longitud": -100.2996,
        "address": "Calle Monte 654",
        "zip_code": "11405",
        "country": "México",
        "state": "Nuevo León",
        "municipality": "Monterrey",
        "city": "San Jerónimo"
    },
    {
        "name": "Plaza del Sol",
        "latitud": 20.6737,
        "longitud": -103.3923,
        "address": "Av. del Sol 987",
        "zip_code": "11405",
        "country": "México",
        "state": "Jalisco",
        "municipality": "Zapopan",
        "city": "Colinas del Sol"
    },
    {
        "name": "Torre Esmeralda",
        "latitud": 19.4318,
        "longitud": -99.1334,
        "address": "Paseo de la Esmeralda 74",
        "zip_code": "11405",
        "country": "México",
        "state": "Ciudad de México",
        "municipality": "Naucalpan de Juárez",
        "city": "Satélite"
    },
    {
        "name": "Playa Paraíso",
        "latitud": 21.1425,
        "longitud": -86.8593,
        "address": "Av. Paraíso 567",
        "zip_code": "11405",
        "country": "México",
        "state": "Quintana Roo",
        "municipality": "Playa del Carmen",
        "city": "Centro"
    },
    {
        "name": "Condominios del Lago",
        "latitud": 19.0184,
        "longitud": -98.2391,
        "address": "Calle del Lago 654",
        "zip_code": "11405",
        "country": "México",
        "state": "Estado de México",
        "municipality": "Metepec",
        "city": "Fraccionamiento del Lago"
    },
    {
        "name": "Estadio Azteca",
        "latitud": 19.3029,
        "longitud": -99.1505,
        "address": "Calzada de Tlalpan 3465",
        "zip_code": "11405",
        "country": "México",
        "state": "Ciudad de México",
        "municipality": "Coyoacán",
        "city": "Santa Úrsula"
    }]

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


async def create_site_devices(db: DBClientProtocol, tenant_info_fixture: dict, data_site: str, multiple_devices: list[Device]):
    await db.init_client()
    siteSchema = Site(**data_site)
    new_site = await db.create_site(tenant="test2", site=siteSchema, origin="test_web")
    output_keys = []
    output_devices = []
    for dev in multiple_devices:
        deviceSchema = Device(**dev)
        dev_ = await db.create_device(tenant="test2", device=deviceSchema, origin='test_web')   
        output_keys.append(dev_.device_key)
        output_devices.append(dev_)
    return new_site[0].site_key, output_keys, new_site[0], output_devices

@pytest.mark.asyncio
async def test_create_minimal_site(db: DBClientProtocol, one_site):
    await db.init_client()
    siteSchema = Site(**one_site)
    output = await db.create_site(tenant="test2", site=siteSchema, origin='test_min_db')
    assert output[0].site_key is not None
    assert isinstance(output[0], Site)

@pytest.mark.asyncio
async def test_create_complete_site(db: DBClientProtocol, complete_site, one_device):
    await db.init_client()
    siteSchema = Site(**complete_site)
    # Create pydantic objects
    countrySchema = Country(name=complete_site["country"])
    stateSchema = State(name=complete_site["state"])
    munSchema = Municipality(name=complete_site["municipality"])
    citySchema = City(name=complete_site["city"])
    # Create country, city, state, municipality in the db
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
    output = await db.create_site(tenant="test2", site=siteSchema, origin='test_site_db')
    assert output[0] is not None
    assert output[0].name == complete_site['name']
    assert isinstance(output[0], Site)


@pytest.mark.asyncio
async def test_list_sites(db: DBClientProtocol, multiple_sites):
    await db.init_client()
    output_sites = []
    # First we create multiple sites
    for element in multiple_sites:
        siteSchema = Site(**element)
        site_ = await db.create_site("test2", siteSchema, 'db_list')
        output_sites.append(site_)
    output = await db.list_sites(tenant="test2")
    assert output['records'] is not None

@pytest.mark.asyncio
async def test_get_site(db: DBClientProtocol, get_site):
    await db.init_client()
    # Create site
    siteSchema = Site(**get_site)
    site = await db.create_site(tenant="test2", site=siteSchema, origin='test_get_db')
    # Get site
    output = await db.get_site(tenant="test2", site_key=site[0].site_key)
    assert output[0].site_key == siteSchema.site_key
    assert output is not None

@pytest.mark.asyncio
async def test_associate_devices(db: DBClientProtocol, multiple_devices_2, data_site_3):
    await db.init_client()
    site_key, output_devices_keys, new_site, devices = await create_site_devices(db, "test2", data_site_3, multiple_devices_2)
    associate = await db.add_devices_to_site("test2", new_site, devices, "test_core")
    assert associate == True

@pytest.mark.asyncio
async def test_disassociate_devices(db: DBClientProtocol, multiple_devices_3, data_site_4):
    await db.init_client()
    site_key, output_devices_keys, new_site, devices = await create_site_devices(db, "test2", data_site_4, multiple_devices_3)
    associate = await db.add_devices_to_site("test2", new_site, devices, "test_core")
    remove = await db.remove_devices_from_site("test2", new_site, devices)
    assert remove == True

# @pytest.mark.asyncio

# @pytest.mark.asyncio
# async def test_delete_site(db: DBClientProtocol, to_delete_site):
#     await db.init_client()
#     # Create Site
#     Site_ = Site(**to_delete_site)
#     create_site = await db.create_site(tenant="test2", site=Site_, origin="edit_test")
#     # Delete Site
#     output = await db.delete_site(tenant="test2", site_key=create_site.site_key)
#     assert output is True