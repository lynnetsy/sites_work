import pytest
import json
import asyncio
from httpx import AsyncClient
from icecream import ic
from string import Template
from device_inventory.models.device_properties import Site
from device_inventory.models.device import Device
from device_inventory.adapters.db.models.hubDevice import HubDevice
from test.fixture import client, actions, asyncApp


@pytest.fixture
def tenant_info_fixture():
    return {
        "hostname": "http://testserver/"
    }

@pytest.fixture
def one_site():
    return {
        "name": "web_site"
    }

@pytest.fixture
def to_delete_site():
    return {
        "name": "del_web_sit"
    }

@pytest.fixture
def complete_site():
    return {
        "name": "web_site",
        "latitud": 70.5,
        "longitud": 80.5,
        "address": "random street 9",
        "country": "Mexico",
        "state": "Ciudad de Mexico",
        "municipality": "Miguel Hidalgo",
        "city": "Anzures",
    }

@pytest.fixture
def edit_minimal_site():
    return {
        "name": "web_min_sit"
    }

@pytest.fixture
def data_site():
    return {
        "name": "wb_site",
        "latitud": 70.5,
        "longitud": 80.5,
        "address": "random web st 10",
        "country": "Mexico",
        "state": "Ciudad de Mexico",
        "municipality": "Miguel Hidalgo",
        "city": "Anzures",
    }

@pytest.fixture
def data_site_2():
    return {
        "name": "dummy_site",
        "latitud": 35.123,
        "longitud": -110.456,
        "address": "123 Main Street",
        "country": "United States",
        "state": "California",
        "municipality": "Los Angeles",
        "city": "Downtown",
    }

@pytest.fixture
def multiple_devices():
    return [
        {
            "vendor": "Apple2",
            "serial_number": "123ABC",
            "status": "ACTIVE"
        },
        {
            "vendor": "Lenovo2",
            "serial_number": "456XYZ",
            "status": "ACTIVE"
        },
        {
            "vendor": "Microsoft2",
            "serial_number": "789DEF",
            "status": "ACTIVE"
        },
        {
            "vendor": "Sony2",
            "serial_number": "012GHI",
            "status": "ACTIVE"
        },
        {
            "vendor": "Samsung2",
            "serial_number": "345JKL",
            "status": "DECOMMISSIONED"
        }
    ]

@pytest.fixture
def multiple_devices_2():
    return [
        {
            "vendor": "Apple",
            "serial_number": "LYNS123",
            "status": "ACTIVE"
        },
        {
            "vendor": "Lenovo",
            "serial_number": "LNV5678",
            "status": "ACTIVE"
        },
        {
            "vendor": "HP",
            "serial_number": "HP9876",
            "status": "ACTIVE"
        },
        {
            "vendor": "Dell",
            "serial_number": "DELL4321",
            "status": "ACTIVE"
        },
        {
            "vendor": "Samsung",
            "serial_number": "SAM6543",
            "status": "DECOMMISSIONED"
        }
    ]

@pytest.fixture
def data_site_3():
    return {
            "name": "Site 2",
            "latitud": 40.7128,
            "longitud": -74.0060,
            "address": "456 Elm St",
            "zip_code": "10001",
            "country": "United States",
            "state": "New York",
            "municipality": "New York City",
            "city": "Manhattan",
        }

@pytest.fixture
def multiple_sites():
    return [
        {
            "name": "Central Park",
            "latitud": 40.785091,
            "longitud": -73.968285,
            "address": "Central Park West & 79th St",
            "zip_code": "10024",
            "country": "United States",
            "state": "New York",
            "municipality": "New York City",
            "city": "Manhattan"
        },
        {
            "name": "Eiffel Tower",
            "latitud": 48.858373,
            "longitud": 2.294481,
            "address": "Champ de Mars, 5 Avenue Anatole France",
            "zip_code": "75007",
            "country": "France",
            "state": "Île-de-France",
            "municipality": "Paris",
            "city": "Paris"
        },
        {
            "name": "Great Wall of China",
            "latitud": 40.431908,
            "longitud": 116.570374,
            "address": "Badaling, Yanqing District",
            "zip_code": "102112",
            "country": "China",
            "state": "Beijing",
            "municipality": "Beijing",
            "city": "Beijing"
        },
        {
            "name": "Sydney Opera House",
            "latitud": -33.8568,
            "longitud": 151.2153,
            "address": "Bennelong Point",
            "zip_code": "2000",
            "country": "Australia",
            "state": "New South Wales",
            "municipality": "Sydney",
            "city": "Sydney"
        },
        {
            "name": "Machu Picchu",
            "latitud": -13.1631,
            "longitud": -72.5450,
            "address": "Machu Picchu",
            "zip_code": "08680",
            "country": "Peru",
            "state": "Cusco",
            "municipality": "Machu Picchu District",
            "city": "Aguas Calientes"
        }
    ]

async def create_site_devices(actions, tenant_info_fixture: dict, data_site: str, multiple_devices: list[Device]):
    siteSchema = Site(**data_site)
    new_site = await actions.create_site(tenant_info=tenant_info_fixture, site=siteSchema, origin="test_web")
    output_keys = []
    for dev in multiple_devices:
        deviceSchema = Device(**dev)
        dev_ = await actions.create_device(tenant_info=tenant_info_fixture, device=deviceSchema, origin='test_web')   
        output_keys.append(dev_.device_key)
    formatted_keys = json.dumps(output_keys)
    return new_site[0].site_key, formatted_keys, output_keys, new_site[0]

@pytest.mark.asyncio
async def test_create_site(asyncApp: asyncApp):
    headers = {
        "tenant": "http://testserver/"
    }
    async with AsyncClient(app=asyncApp, base_url="http://") as ac:
        query= """
        mutation create_site {
    create_site(name: "s_graphql", latitud: 80, longitud: 40, address: "Gabriel Mancera 80", zip_code: "11700", origin: "create_grap") {
        errors
        edge{
        cursor
        node {
            site_key
            name
            latitud
            longitud
            address
        }
        }
    }
    }
"""
        response = await ac.post("/api/v2/graphql/", json={"query": query}, headers=headers)
    ic(response.json())
    assert response.status_code == 200
    response_body = response.json()
    assert response_body['data']['create_site']['edge']['cursor'] is not None
    assert response_body['data']['create_site']['errors'] == None

@pytest.mark.asyncio
async def test_associate_devices_to_site(asyncApp: asyncApp, data_site, multiple_devices, actions, tenant_info_fixture):
    site_key, formatted_keys, output_keys, new_site = await create_site_devices(actions, tenant_info_fixture, data_site, multiple_devices)
    headers = {
        "tenant": "http://testserver/"
    }
    async with AsyncClient(app=asyncApp, base_url="http://") as ac:
        query= f"""
        mutation associate_device_to_site {{
        associate_device_to_site(site_key:"{site_key}", devices: {formatted_keys}, origin: "test_web"){{
            success,
            errors,
            edge{{
                cursor
                node {{
                    site_key
                    name
                    latitud
                    longitud
                    address
                    zip_code
                    country
                    state
                    municipality
                    city
                    devices {{
                        device_key
                        vendor
                        serial_number
                    }}
                }}
            }}
        }}
    }}
    """
        response = await ac.post("/api/v2/graphql/", json={"query": query}, headers=headers)
    assert response.status_code == 200
    response_body = response.json()
    success = response_body['data']['associate_device_to_site']['success']
    assert success == True
    response_site_key = response_body['data']['associate_device_to_site']['edge']['cursor']
    assert response_site_key == site_key

@pytest.mark.asyncio
async def test_disassociate_devices_to_site(asyncApp: asyncApp, data_site_2, multiple_devices_2, actions, tenant_info_fixture):
    #First create site and devices, this fnc return site key and keys devices with format json and just keys.
    site_key, formatted_keys, output_keys, new_site = await create_site_devices(actions, tenant_info_fixture, data_site_2, multiple_devices_2)
    ic(new_site)
    # First associate devices we need the models not the keys
    models_dev = await actions.keys_to_models(tenant_info_fixture, output_keys, Device, HubDevice, 'hub_device_key')
    add = await actions.add_devices_to_site(tenant_info_fixture, new_site, models_dev, "site_web")
    ic(add)
        
    headers = {
        "tenant": "http://testserver/"
    }
    async with AsyncClient(app=asyncApp, base_url="http://") as ac:
        query= f"""
        mutation disassociate_device_from_site {{
    disassociate_device_from_site(site_key:"{site_key}", devices: {formatted_keys}){{
        success,
        errors,
        # page_info,
        edge{{
            cursor
            node {{
                site_key
                name
                latitud
                longitud
                address
                zip_code
                country
                state
                municipality
                city
                devices {{
                    device_key
                }}
            }}
        }}
    }}
}}
"""
        response = await ac.post("/api/v2/graphql/", json={"query": query}, headers=headers)
    assert response.status_code == 200
    response_body = response.json()
    success = response_body['data']['disassociate_device_from_site']['success']
    assert success == True
    response_site_key = response_body['data']['disassociate_device_from_site']['edge']['cursor']
    assert response_site_key == site_key

@pytest.mark.asyncio
async def test_get_site(asyncApp: asyncApp, data_site_3, actions, tenant_info_fixture):
    # Create site
    siteSchema = Site(**data_site_3)
    site = await actions.create_site(tenant_info=tenant_info_fixture, site=siteSchema, origin='web_get')
    # Get site
    headers = {
        "tenant": "http://testserver/"
    }
    async with AsyncClient(app=asyncApp, base_url="http://") as ac:
        query=f"""query site {{
  site(site_key:"{site[0].site_key}") {{
    errors
    edge {{
      cursor
      node {{
        site_key
        name
        latitud
        longitud
        address
      }}
    }}
    }}}}

    """
        response = await ac.post("/api/v2/graphql/", json={"query": query}, headers=headers)
    assert response.status_code == 200
    response_body = response.json()
    ic(response_body)
    assert site[0].site_key == response_body['data']['site']['edge']['cursor']

@pytest.mark.asyncio
async def test_list_sites(asyncApp: asyncApp, multiple_sites, actions, tenant_info_fixture):
    output_sites = []
    # First we create multiple sites
    for element in multiple_sites:
        siteSchema = Site(**element)
        site_ = await actions.create_site(tenant_info_fixture, siteSchema, 'web_list')
        output_sites.append(site_)
     # List Sites
    headers = {
        "tenant": "http://testserver/"
    }
    async with AsyncClient(app=asyncApp, base_url="http://") as ac:
        query="""
        query sites {
  sites(
    page: 1,
    items: 3,
  ) {
    errors
    page_info {
      page_number
      total_pages
      has_previous_page
      has_next_page
    }
    edges {
      cursor
      node {
        site_key
        name
        latitud
        longitud
        address
      }
    }
  }
}"""
        response = await ac.post("/api/v2/graphql/", json={"query": query}, headers=headers)
    assert response.status_code == 200
    response_body = response.json()
    ic(response_body)
    assert response_body['data']['sites']['edges'] is not None


    