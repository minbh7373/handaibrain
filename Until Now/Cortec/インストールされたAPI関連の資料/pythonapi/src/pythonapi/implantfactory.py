#######################################################################
# Copyright 2015-2019, CorTec GmbH
# All rights reserved.
#
# Redistribution, modification, adaptation or translation is not permitted.
#
# CorTec shall be liable a) for any damage caused by a willful, fraudulent or grossly 
# negligent act, or resulting in injury to life, body or health, or covered by the 
# Product Liability Act, b) for any reasonably foreseeable damage resulting from 
# its breach of a fundamental contractual obligation up to the amount of the 
# licensing fees agreed under this Agreement. 
# All other claims shall be excluded. 
# CorTec excludes any liability for any damage caused by Licensee's 
# use of the Software for regular medical treatment of patients.
#######################################################################
'''@doctring implantfactory

    Device discovery and factory interface creating implant handles to
    control implant devices.

    Main responsiblities of this component:
    - discovering all external units and implants connected to the 
        system which are recognized by the factory
    - creating an instance of a suitable hardware abstraction layer 
        implementation for a specified external unit and implant
        combination.
'''

from ctypes import create_string_buffer, c_size_t, c_bool, POINTER, pointer, byref 
from typing import List

from pythonapi.pythonapibase import get_api_base, CAPIStatus, opaque_ptr, _Opaque, get_error_message
from pythonapi.externalunitinfo import ExternalUnitInfo, _ExternalUnitInfoVector
from pythonapi.implantinfo import ImplantInfo
from pythonapi.implant import Implant

def init_implant_factory(enable_logging: bool, file_name: str):
    '''
        Initialize library. Must be called before calling any other
        library function.

        If enable logging is turned on, all events (e.g. measurement
        channel data, implant status, etc.) received from the implant
        are logged into a binary log file.
    '''

    api = get_api_base()

    implantfactory_init = api.dll_instance.implantfactory_init
    implantfactory_init.restype = CAPIStatus

    buffer_length = len(file_name)
    buffer = create_string_buffer(buffer_length)
    buffer.value = file_name.encode('utf-8')

    status = implantfactory_init(enable_logging, buffer, c_size_t(buffer_length))

    if status != CAPIStatus.STATUS_OK:
        raise RuntimeError(f"{status.name}: {api.error_message}")

class ImplantFactory():
    def __init__(self):
        api = get_api_base()

        implantfactory_getFactoryHandle = api.dll_instance.implantfactory_getFactoryHandle
        implantfactory_getFactoryHandle.restype = CAPIStatus
        implantfactory_getFactoryHandle.argtypes = [POINTER(opaque_ptr)]

        self._handle = pointer(_Opaque())

        vector_size = 127
        vector_t = POINTER(_Opaque) * vector_size
        self._external_unit_infos = _ExternalUnitInfoVector(c_size_t(vector_size), pointer(vector_t()[0]))

        status = implantfactory_getFactoryHandle(byref(self._handle))

        if status != CAPIStatus.STATUS_OK:
            raise RuntimeError(f"Could not create an implant factory due to error: {status.name}")

        self.__registerMethods(api)

    def __registerMethods(self, api):
        '''Register DLL methods used by this class.'''

        self._implantfactory_getExternalUnitInfos = api.dll_instance.implantfactory_getExternalUnitInfos
        self._implantfactory_getExternalUnitInfos.restype = CAPIStatus
        self._implantfactory_getExternalUnitInfos.argtypes = [opaque_ptr, POINTER(_ExternalUnitInfoVector)]
        
        self._implantfactory_getImplantInfo = api.dll_instance.implantfactory_getImplantInfo
        self._implantfactory_getImplantInfo.restype = CAPIStatus
        self._implantfactory_getImplantInfo.argtypes = [opaque_ptr, opaque_ptr, POINTER(opaque_ptr)]
                
        self._implantfactory_isResponsibleFactory = api.dll_instance.implantfactory_isResponsibleFactory
        self._implantfactory_isResponsibleFactory.restype = CAPIStatus
        self._implantfactory_isResponsibleFactory.argtypes = [opaque_ptr, opaque_ptr, POINTER(c_bool)]
                        
        self._implantfactory_create = api.dll_instance.implantfactory_create
        self._implantfactory_create.restype = CAPIStatus
        self._implantfactory_create.argtypes = [opaque_ptr, opaque_ptr, opaque_ptr, POINTER(opaque_ptr)]
        
    def load_external_unit_infos(self) -> List[ExternalUnitInfo]:
        '''Method for discovering the available external units
            connected to the system.
        '''

        status = self._implantfactory_getExternalUnitInfos(self._handle, byref(self._external_unit_infos))

        if status == CAPIStatus.STATUS_OK:
            return self._convert_to_external_unit_infos()
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")

    def _convert_to_external_unit_infos(self):
        '''Convert the C data structure to python objects.'''

        return [ExternalUnitInfo(self._external_unit_infos.vector[i]) for i in range(self._external_unit_infos.count)]
        
    def load_implant_info(self, ext_unit_info: ExternalUnitInfo) -> ImplantInfo:
        '''Method for discovering the connected implant of an
            external unit.

           @param ext_unit_info (Type: ExternalUnitInfo) The 
                external unit for which connected implants should be
                found.
        '''

        implant_info = pointer(_Opaque())

        status = self._implantfactory_getImplantInfo(self._handle, ext_unit_info._handle, byref(implant_info))

        if status == CAPIStatus.STATUS_OK:
            return ImplantInfo(implant_info)
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")

    def is_responsible_factory(self, ext_unit_info: ExternalUnitInfo) -> bool:
        '''Determine if the factory is responsible for a certain
            external unit.

           @param ext_unit_info (Type: ExternalUnitInfo) The external
                unit for which the factory is checked.
        '''

        is_responsible = c_bool(False)

        status = self._implantfactory_isResponsibleFactory(self._handle, ext_unit_info._handle, byref(is_responsible))

        if status == CAPIStatus.STATUS_OK:
            return is_responsible.value
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")

    def create(self, ext_unit_info: ExternalUnitInfo, implant_info: ImplantInfo) -> Implant:
        '''Creates an initialized implant handle for the device
            combination specified by implantId and externalUnitId.

           @param ext_unit_info (Type: ExternalUnitInfo) The external
                unit to which a connection should be established.
           @param implant_info  (Type: ImplantInfo)      The implant
                to which a connection should be established.
        '''

        implant = pointer(_Opaque())

        status = self._implantfactory_create(self._handle, ext_unit_info._handle, implant_info._handle, byref(implant))

        if status == CAPIStatus.STATUS_OK:
            return Implant(implant)
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")
    