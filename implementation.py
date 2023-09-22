async def list_sites(self, tenant: str, page: int = 0, limit: int = -1, col_sort: list[str] = [], col_order: list[str] = []) -> List[Site]:
        """The list_sites function returns a list of sites for the given tenant.

        Args:
            self: Access attributes and methods of the class in which it is used
            tenant:str: Specify the tenant that we want to list sites for
            page:int=0: Specify the page number of the results to be returned
            limit:int=-1: Specify how many sites to return

        Returns:
            A list of site objects

        Doc Author:
            Trelent
        """
        schema = await self.get_tenant_schema(tenant)
        if schema is None:
            raise TenantNotFound()

        async with self.__session() as session:
            await session.connection(execution_options={"schema_translate_map": {"TENANT_NAME": schema}})

            try:

                # Get the metrics for the query
                count_query = select(func.count('*')).order_by(None).select_from(HubSite)
                count_results = await session.execute(count_query)
                count = count_results.scalars().first()
                expected_pages = count / limit
                if(page > expected_pages and page > 0):
                    raise ValueError(
                        "The page number is higher than the expected pages."
                    )

                query = select(HubSite)

                # Validate columns sort
                if len(col_sort) != len(col_order):
                    raise ValueError(
                        "The col_sort and col_order lists must have the same length."
                    )

                # Sort data if is need it
                if(col_sort):
                    order_functions = []
                    # Merge both lists and loop through them.
                    for column, direction in zip(col_sort, col_order):

                        if(hasattr(HubSite,column)):
                            attr = getattr(HubSite, column)
                        else:
                            if(hasattr(SatSite,column) == False):
                                raise ProcessingError('Site has no attribute ' + column)

                            attr = getattr(SatSite, column)

                        order = desc(attr) if direction == 'DESC' else asc(attr)

                        order_functions.append(order)

                    query = query.join(HubSite.sat_info)
                    query = query.order_by(*order_functions)

                # Paginate data
                if limit > 0:
                    query = query\
                        .limit(limit)\
                        .offset(page * limit)

                results = await session.execute(query)
                result_list = []
                for site in results.scalars().unique():
                    devices_keys = [device.HUB_DEVICE_HUB_DEVICE_KEY for device in site.linked_devices]
                    associate_devices = await self.get_multiple_devices(tenant, devices_keys)
                    # if site.sat_info and site.sat_info.SAT_LOAD_DATE != site.sat_info.LOAD_END_DATE:
                    #     continue
                    site = Site(
                        site_key=site.HUB_SITE_KEY,
                        name=site.NAME,
                        latitud=site.sat_info.LATITUD if site.sat_info is not None else None,
                        longitud=site.sat_info.LONGITUD if site.sat_info is not None else None,
                        address=site.sat_info.ADDRESS if site.sat_info is not None else None,
                        zip_code=site.sat_info.ZIP_CODE if site.sat_info is not None else None,
                        country=site.site_info.hub_country.NAME if site.site_info is not None else None,
                        state=site.site_info.hub_state.NAME if site.site_info is not None else None,
                        municipality=site.site_info.hub_municipality.NAME if site.site_info is not None else None,
                        city=site.site_info.hub_city.CITY if site.site_info is not None else None,
                        )
                    result_dict = {
                        "site": site
                    }
                    if associate_devices:
                        result_dict["devices"] = associate_devices
                    result_list.append(result_dict)
                return {
                    'records' : result_list,
                    'total_records' : count
                }
            except Exception as e:
                self.logger.error(e)
                if(isinstance(e,ProcessingError)):
                    raise e
                if(isinstance(e,ValueError)):
                    raise e
                return {
                    'records' : [],
                    'total_records' : 0
                }

    async def get_site(self, tenant: str, site_key: str) -> Tuple[Site, List[Device]]:
        """The get_site function returns a Site object for the specified tenant and site key.

        Args:
            self: Access the class attributes
            tenant:str: Specify the tenant that we want to get a site from
            site_key:str: Specify the site to be retrieved

        Returns:
            A site object

        Doc Author:
            Trelent
        """
        schema = await self.get_tenant_schema(tenant)
        if schema is None:
            raise TenantNotFound()

        async with self.__session() as session:
            await session.connection(execution_options={"schema_translate_map": {"TENANT_NAME": schema}})
            try:
                options = [
                    selectinload(HubSite.sat_info),
                    selectinload(HubSite.linked_devices).\
                        selectinload(LinkSiteDevice.device).\
                        selectinload(HubDevice.device_gen_info),
                    selectinload(HubSite.linked_devices).\
                        selectinload(LinkSiteDevice.device).\
                        selectinload(HubDevice.ssh_config),
                    selectinload(HubSite.site_info).\
                        selectinload(LinkSiteCountryStateMunicipality.hub_country),
                    selectinload(HubSite.site_info).\
                        selectinload(LinkSiteCountryStateMunicipality.hub_state),
                    selectinload(HubSite.site_info).\
                        selectinload(LinkSiteCountryStateMunicipality.hub_municipality),
                    selectinload(HubSite.site_info).\
                        selectinload(LinkSiteCountryStateMunicipality.hub_city)
                ]

                query = select(
                        HubSite
                    ).where(
                        HubSite.HUB_SITE_KEY == site_key
                    ).options(*options)
                results = await session.execute(query)
                result = results.scalars().first()
                if result is None:
                    self.logger.info('Site does not exists')
                    return None
                output_site = Site(
                            site_key=result.HUB_SITE_KEY,
                            name=result.NAME,
                            latitud=result.sat_info.LATITUD if result.sat_info is not None else None,
                            longitud=result.sat_info.LONGITUD if result.sat_info is not None else None,
                            address=result.sat_info.ADDRESS if result.sat_info is not None else None,
                            zip_code=result.sat_info.ZIP_CODE if result.sat_info is not None else None,
                            country=result.site_info.hub_country.NAME if result.site_info is not None else None,
                            state=result.site_info.hub_state.NAME if result.site_info is not None else None,
                            municipality=result.site_info.hub_municipality.NAME if result.site_info is not None else None,
                            city=result.site_info.hub_city.CITY if result.site_info is not None else None
                        )      
                devices = []
                for linked_device in result.linked_devices:
                    dev = linked_device.device  # Acceder a la relación device para cada LinkedDevice
                    if dev:
                        output_device = Device(
                            vendor=dev.VENDOR if dev is not None else None,
                            serial_number=dev.SERIAL_NUMBER if dev is not None else None,
                            hostname=dev.device_gen_info.HOSTNAME if dev.device_gen_info is not None else None,
                            description=dev.device_gen_info.DESCRIPTION if dev.device_gen_info is not None else None,
                            status=dev.device_gen_info.STATUS if dev.device_gen_info is not None else None,
                            cypher=dev.ssh_config.CYPHER if dev.ssh_config is not None else None,
                            host_key_algorithm=dev.ssh_config.HOST_KEY_ALGORITHM if dev.ssh_config is not None else None,
                            mac=dev.ssh_config.MAC if dev.ssh_config is not None else None,
                            device_type=dev.ssh_config.DEVICE_TYPE if dev.ssh_config is not None else None,
                            )
                        devices.append(output_device)
                return output_site, devices
            except Exception as e:
                # TODO: Mejorar las excepciones de aca!
                ic(e)
                if isinstance(e, ConnectionRefusedError):
                    self.logger.error(f'Can\'t connect to server:\n{e}')
                    return None
                self.logger.error(f'Can\'t find site for {site_key}, because:\n{e}')
                return None

    async def create_site(self, tenant: str, site: Site, origin: str) -> Site:
        """The create_site function creates a new site in the specified tenant.

        Args:
            self: Access the class attributes and methods
            tenant:str: Specify the tenant that will be used for the site
            site:Site: Pass in the site object that is being created
            origin:str: Specify the origin of the record

        Returns:
            A site object

        Doc Author:
            Trelent
        """
        if (site.latitud is None and site.longitud is not None) or (site.latitud is not None and site.longitud is None):
            raise CoordinatesError('Latitude or longitude not defined')

        schema = await self.get_tenant_schema(tenant)
        if schema is None:
            raise TenantNotFound()

        now = datetime.now()
        async with self.__session() as session:
            async with session.begin():
                await session.connection(execution_options={"schema_translate_map": {"TENANT_NAME": schema}})
                try:
                    self.logger.debug('Creating HubSite object')
                    new_site = HubSite(
                        HUB_SITE_KEY=site.site_key,
                        NAME=site.name,
                        HUB_RECORD_SRC=origin,
                        HUB_LOAD_DATE=now
                    )
                    self.logger.debug(f'Adding Site {new_site}')
                    session.add(new_site)
                    if site.address is not None or (site.latitud is not None and site.longitud is not None):
                        self.logger.debug('Creating SatSite object')
                        new_sat = SatSite(
                            HUB_SITE_KEY=site.site_key,
                            LATITUD=site.latitud,
                            LONGITUD=site.longitud,
                            ADDRESS=site.address,
                            ZIP_CODE=site.zip_code,
                            SAT_RECORD_SRC=origin,
                            SAT_LOAD_DATE=now,
                            LOAD_END_DATE=now,
                        )
                        session.add(new_sat)
                        self.logger.debug(f'New SatSite {new_sat}')
                    if site.country is not None and site.state is not None \
                        and site.municipality is not None and site.city is not None:
                        country = await self.get_country_by_name(tenant, site.country)
                        state = await self.get_state_by_name(tenant, site.state)
                        mun = await self.get_municipality_by_name(tenant, site.municipality)
                        city = await self.get_city_by_name(tenant, site.city)
                        if country is not None and state is not None \
                            and mun is not None and city is not None:
                            new_link = LinkSiteCountryStateMunicipality(
                                HUB_SITE_HUB_SITE_KEY=site.site_key,
                                HUB_COUNTRY_HUB_COUNTRY_KEY=country.country_key,
                                HUB_STATE_HUB_STATE_KEY=state.state_key,
                                HUB_MUNICIPALITY_HUB_MUNICIPALITY_KEY=mun.municipality_key,
                                HUB_CITY_HUB_CITY_KEY=city.city_key,
                                LINK_LOAD_DATE=now,
                                LINK_END_DATE=now,
                                LINK_RECORD_SRC=origin
                            )
                            session.add(new_link)
                            self.logger.debug(f'New LinkSiteCountryStateMunicipality created: {new_link}')
                except Exception as e:
                    # TODO: Mejorar las excepciones de aca!
                    if isinstance(e, ConnectionRefusedError):
                        self.logger.error(f'Can\'t connect to server:\n{e}')
                    elif isinstance(e, IntegrityError):
                        self.logger.error(f'Can\'t create site:\n({site}), because:\nThe site already exist')
                    else:
                        self.logger.error(f'Can\'t create site:\n({site}), because:\n{e}')
                    return None
            
            return await self.get_site(tenant, site.site_key)

    async def edit_site(self, tenant: str, site_key: str, site: Site, origin: str) -> Site:
        """The edit_site function will update the site with the given id.

        Args:
            self: Access the class attributes
            tenant:str: Specify the tenant that is being edited
            site:Site: Specify the site that will be edited
            origin:str: Specify the origin of the record

        Returns:
            A site object

        Doc Author:
            Trelent
        """
        schema = await self.get_tenant_schema(tenant)
        if schema is None:
            raise TenantNotFound()

        async with self.__session() as session:
            async with session.begin():
                await session.connection(execution_options={"schema_translate_map": {"TENANT_NAME": schema}})
                try:
                    query = select(HubSite).where(HubSite.HUB_SITE_KEY == site_key)
                    results = await session.execute(query)
                    site_result = results.scalars().first()

                    query = select(SatSite).where(and_(
                        SatSite.HUB_SITE_KEY == site_key,
                        SatSite.SAT_LOAD_DATE == SatSite.LOAD_END_DATE
                    ))
                    results = await session.execute(query)
                    site_data_result = results.scalars().first()

                    # If we don't had data in SatSite
                    if site_data_result is None:
                        now = datetime.now()
                        new_site_data = SatSite(
                            HUB_SITE_KEY=site_key,
                            LATITUD=site.latitud,
                            LONGITUD=site.longitud,
                            ADDRESS=site.address,
                            SAT_LOAD_DATE=now,
                            LOAD_END_DATE=now,
                            SAT_RECORD_SRC=origin
                        )
                        session.add(new_site_data)
                        await session.commit()
                        
                    else:
                        change = False

                        if site_data_result.LATITUD != site.latitud:
                            change = True
                        if site_data_result.LONGITUD != site.longitud:
                            change = True
                        if site_data_result.ADDRESS != site.address:
                            change = True

                        if change:
                            now = datetime.now()
                            new_site_data = SatSite(
                                HUB_SITE_KEY=site.site_key,
                                SAT_LOAD_DATE=now,
                                LATITUD=site.latitud if site.latitud is not None else None,
                                LONGITUD=site.longitud if site.longitud is not None else None,
                                ADDRESS=site.address if site.address is not None else None,
                                LOAD_END_DATE=now,
                                SAT_RECORD_SRC=origin
                            )
                            # ATENCION:
                            # Ojo con esto, estoy dejando que el cambio se realice cuando la sesión termine y el sqlalchemy
                            # haga el commit. No sé si esto es lo más óptimo.
                            session.add(new_site_data)
                            await session.commit()
                except Exception as e:
                    self.logger.error(f'Exception:\n{e}')
                    return None
                
                return await self.get_site(tenant=tenant, site_key=site.site_key)

    async def delete_site(self, tenant: str, site_key: str) -> None:
        """The delete_site function deletes a site from the database.

        Args:
            self: Access the class attributes and methods
            tenant:str: Specify the tenant name
            site_key:str: Identify the site to be deleted

        Returns:
            None

        Doc Author:
            Trelent
        """
        schema = await self.get_tenant_schema(tenant)
        if schema is None:
            raise TenantNotFound()

        async with self.__session() as session:
            async with session.begin():
                await session.connection(execution_options={"schema_translate_map": {"TENANT_NAME": schema}})
                try:
                    query = select(HubSite).where(HubSite.HUB_SITE_KEY == site_key)
                    results = await session.execute(query)
                    site_result = results.scalars().first()

                    query = select(SatSite).where(and_(
                        SatSite.HUB_SITE_KEY == site_key,
                        SatSite.SAT_LOAD_DATE == SatSite.LOAD_END_DATE
                    ))
                    results = await session.execute(query)
                    site_data_result = results.scalars().first()

                    # If we don't had data in SatSite

                    if site_result and site_data_result is not None:
                        now = datetime.now()
                        site_data_result.LOAD_END_DATE = now
                        await session.commit()
                        return True
                except Exception as e:
                    ic(e)
                    self.logger.error(f'Exception:\n{e}')
                return None

async def add_devices_to_site(self, tenant: str, site: Site, devices: List[Device], origin: str) -> bool:
        """
        Buscando el schema del tenant
        """

        schema = await self.get_tenant_schema(tenant)
        if schema is None:
            raise TenantNotFound()

        """Iniciando sesión"""
        async with self.__session() as session:
            async with session.begin():
                await session.connection(execution_options={"schema_translate_map": {"TENANT_NAME": schema}})
                """Buscar el pais en la DB"""
                try:
                    query = select(HubSite).where(
                        HubSite.HUB_SITE_KEY == site.site_key
                    ).options(
                        defaultload(HubSite.linked_devices)
                    )
                    results = await session.execute(query)
                    db_site = results.scalars().first()
                    if db_site is None:
                        """Si el pais no existe mensaje de error y levantar excepción"""
                        self.logger.error(f'Site {site} does not exist')
                        raise ItemDoesNotExist()
                except Exception as e:
                    """
                    Se vuelve a levantar el error por que estaba dentro de un try.
                    TODO: Esto tiene que poder ser mejorable, creo, por que ahora esta horrible.
                    """
                    if isinstance(e, ItemDoesNotExist):
                        raise e
                    self.logger.error(f"{e!r}")

                """Ahora armemos un listado de los ids de los estados"""
                device_ids = []
                for device in devices:
                    device_ids.append(device.device_key)

                """Busquemos  esos ids en la DB"""
                try:
                    count_query_devices = select(func.count('*')).where(
                        HubDevice.HUB_DEVICE_KEY.in_(device_ids)
                    ).order_by(None).select_from(HubDevice)
                    query_devices = select(HubDevice).where(
                        HubDevice.HUB_DEVICE_KEY.in_(device_ids)
                    ).order_by(None)
                    count_results_devices = await session.execute(count_query_devices)
                    results_devices = await session.execute(query_devices)
                    db_devices_count = count_results_devices.scalars().first()
                except Exception as e:
                    self.logger.error(f"Error {e!r}")

                """Si la cantidad de ids que estamos buscando no es igual a la que la base de datos retorna, error."""
                if db_devices_count != len(device_ids):
                    raise ItemDoesNotExist(
                        f"One of the devices does not exist, devices parameter count {len(device_ids)},"
                        f" database devices returned {db_devices_count}"
                    )

                """Ya se habian agregado estos estados al pais?"""
                try:
                    check_devices_query = select(func.count('*')).where(
                        and_(
                                LinkSiteDevice.HUB_SITE_HUB_SITE_KEY == site.site_key,
                                LinkSiteDevice.HUB_DEVICE_HUB_DEVICE_KEY.in_(device_ids),
                                LinkSiteDevice.LINK_LOAD_DATE == LinkSiteDevice.LINK_END_DATE
                        )
                    ).order_by(None).select_from(LinkSiteDevice)
                    check_devices_results = await session.execute(check_devices_query)
                    check_devices_count = check_devices_results.scalars().first()

                    if check_devices_count > 0:
                        raise ItemAlreadyExist(
                            f"Some of the devices already exist, database devices returned {check_devices_count}"
                        )
                except Exception as e:
                    if isinstance(e, ItemAlreadyExist):
                        raise e
                    self.logger.error(f"{e!r}")

                linked_devices = []
                now = datetime.now()
                for result_device in results_devices.unique().scalars():
                    tmp_lnkd_site = LinkSiteDevice(
                        HUB_SITE_HUB_SITE_KEY=db_site.HUB_SITE_KEY,
                        HUB_DEVICE_HUB_DEVICE_KEY=result_device.HUB_DEVICE_KEY,
                        LINK_LOAD_DATE=now,
                        LINK_END_DATE=now,
                        LINK_RECORD_SRC=origin
                    )
                    linked_devices.append(tmp_lnkd_site)
                try:
                    session.add_all(linked_devices)
                    await session.commit()
                except Exception as e:
                    self.logger.error(f"{e!r}")
            """
            No se si esta es la forma de hacerlo :think 
            """
            async with session.begin():
                await session.connection(execution_options={"schema_translate_map": {"TENANT_NAME": schema}})
                check_devices_query = select(func.count('*')).where(
                    and_(
                        LinkSiteDevice.HUB_SITE_HUB_SITE_KEY == site.site_key,
                        LinkSiteDevice.HUB_DEVICE_HUB_DEVICE_KEY.in_(device_ids),
                        LinkSiteDevice.LINK_LOAD_DATE == LinkSiteDevice.LINK_END_DATE
                    )
                ).order_by(None).select_from(LinkSiteDevice)
                check_devices_results = await session.execute(check_devices_query)
                check_devices_count = check_devices_results.scalars().first()

                if check_devices_count != len(device_ids):
                    raise ProcessingError(
                        f"Couldn't add all devices to the site."
                    )

                return True

    async def remove_devices_from_site(self, tenant: str, site: Site, devices: List[Device]) -> bool:
        schema = await self.get_tenant_schema(tenant)
        if schema is None:
            raise TenantNotFound()

        async with self.__session() as session:
            async with session.begin():
                await session.connection(execution_options={"schema_translate_map": {"TENANT_NAME": schema}})
                try:
                    """Checar si el site existe"""
                    query_count_site = select(func.count('*')).select_from(HubSite).where(
                        HubSite.HUB_SITE_KEY == site.site_key
                    ).order_by(None)

                    site_count_results = await session.execute(query_count_site)
                    site_count = site_count_results.scalars().first()
                    if site_count == 0:
                        raise ItemDoesNotExist(f'The site {site} does not exist.')
                except Exception as e:
                    self.logger.error(e)
                    if isinstance(e, ItemDoesNotExist):
                        raise e

                """Checar si los devices existen"""
                try:
                    devices_ids = []
                    for device in devices:
                        devices_ids.append(device.device_key)
                    query_check_devices_count = select(func.count('*')).select_from(HubDevice).where(
                        HubDevice.HUB_DEVICE_KEY.in_(devices_ids)
                    ).order_by(None)
                    results_check_devices_count = await session.execute(query_check_devices_count)
                    check_devices_count = results_check_devices_count.scalars().first()
                    if check_devices_count != len(devices):
                        raise ItemDoesNotExist(
                            f"One of the devices does not exist, devices parameter count {len(devices)},"
                            f" database devices returned {check_devices_count}"
                        )
                except Exception as e:
                    self.logger.error(e)
                    if isinstance(e, ItemDoesNotExist):
                        raise e

                """Check if all the devices on list are associated with the site"""
                try:
                    query_check_added_devices_count = select(func.count('*')).select_from(LinkSiteDevice).where(
                        and_(
                            LinkSiteDevice.HUB_SITE_HUB_SITE_KEY == site.site_key,
                            LinkSiteDevice.HUB_DEVICE_HUB_DEVICE_KEY.in_(devices_ids),
                            LinkSiteDevice.LINK_LOAD_DATE == LinkSiteDevice.LINK_END_DATE
                        )
                    ).order_by(None)
                    results_check_added_devices_count = await session.execute(
                        query_check_added_devices_count
                    )
                    check_added_devices_count = results_check_added_devices_count.scalars().first()
                    if check_added_devices_count < len(devices):
                        raise ProcessingError(
                            f"One of the devices is not associated with the site, devices parameter "
                            f"count {len(devices)}, database devices returned "
                            f"{check_added_devices_count}"
                        )
                except Exception as e:
                    self.logger.error(e)
                    raise e

                """Cambiar el campo load_end_date para que adquieran el estado borrado"""
                try:
                    query_get_devices = select(LinkSiteDevice).where(and_(
                        LinkSiteDevice.HUB_SITE_HUB_SITE_KEY == site.site_key,
                        LinkSiteDevice.HUB_DEVICE_HUB_DEVICE_KEY.in_(devices_ids)
                    )).order_by(None)
                    now = datetime.now()
                    results_get_devices = await session.execute(query_get_devices)
                    for result_device in results_get_devices.unique().scalars():
                        result_device.LINK_END_DATE = now
                    await session.commit()
                    return True
                except Exception as e:
                    self.logger.error(e)
                    return False
    # Este metodo funciona sobretodo para los endpoints donde solamente recibimos una lista de llaves
    async def keys_to_models(self, tenant: str, keys: Type[List], pydantic_model: Type[T], sqlalchemy_model: Type[U], sqlalchemy_field: str) -> List[T]:
        schema = await self.get_tenant_schema(tenant)
        if schema is None:
            raise TenantNotFound()

        async with self.__session() as session:
            async with session.begin():
                await session.connection(execution_options={"schema_translate_map": {"TENANT_NAME": schema}})
                try:
                    field_upper = str(sqlalchemy_field.upper())
                    model = getattr(sqlalchemy_model, field_upper)
                    query = select(sqlalchemy_model).where(model.in_(keys)
                    ).order_by(None)
                    results_query = await session.execute(query)
                    check_results = results_query.unique().all()
                    
                    pydantic_fields = pydantic_model.__annotations__
                    sqlalchemy_columns = sqlalchemy_model.__table__.columns.keys()
                    # Aqui llamo a las llaves que estan distintas entre
                    # pydantic y sqlalchemy
                    pydantic_field = f"{pydantic_model.__name__.lower()}_key"
                    hub_key_field = f"HUB_{pydantic_model.__name__.upper()}_KEY"

                    # Aca obtengo todas las llaves de mi objeto pydantic
                    # Puede ser cualquier objeto
                    keys = [key for key in pydantic_fields.keys()]
                    pydantic_instances = []

                    #Aca hacemos un for por cada resultado de sqlalchemy
                    for result in check_results:
                        mapped_data = {
                            key: getattr(result[0], db_field)  # Acceso al valor del atributo usando getattr
                            for (key, db_field) in islice(zip(keys[1:], sqlalchemy_columns[1:]), len(sqlalchemy_columns)) \
                                if not isinstance(getattr(result[0], db_field), datetime)
                        }
                    
                        # Aca vamos a llenar el diccionario con su llave personalizada
                        # device_key = result[0].HUB_{PYDANTIC_MODEL}_KEY
                        hub_device_key = getattr(result[0], hub_key_field, None)
                        mapped_data[f"{pydantic_field}"] = hub_device_key
                        pydantic_instance = pydantic_model(**mapped_data)  # Crear instancia Pydantic
                        pydantic_instances.append(pydantic_instance)

                    return pydantic_instances
                except Exception as e:
                    self.logger.error(e)
                    return None

        # TODO: Falta checar que devuelva de cualquier relacion 