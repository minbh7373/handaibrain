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
'''@doctring externalunitinfo

    Information about the external unit.
'''
from ctypes import create_string_buffer, c_size_t, Structure, POINTER, byref, pointer
from pythonapi.pythonapibase import get_api_base, CAPIStatus, c_size_t_ptr, opaque_ptr, get_error_message

class _ExternalUnitInfoVector(Structure):
    '''Ctype for an external unit info vector.'''

    _fields_ = [("count", c_size_t), 
                ("vector", POINTER(opaque_ptr))]

class ExternalUnitInfo():
    '''
        Class holding information about a connected external unit.

        Create instances using the implant factory!
    '''

    def __init__(self, handle):
        self._handle = handle

        api = get_api_base()

        self._externalunitinfo_getImplantType = api.dll_instance.externalunitinfo_getImplantType
        self._externalunitinfo_getImplantType.restype = CAPIStatus

        self._externalunitinfo_getDeviceId = api.dll_instance.externalunitinfo_getDeviceId
        self._externalunitinfo_getDeviceId.restype = CAPIStatus
        
        self._externalunitinfo_getFirmwareVersion = api.dll_instance.externalunitinfo_getFirmwareVersion
        self._externalunitinfo_getFirmwareVersion.restype = CAPIStatus

        self._externalunitinfos_destroy = api.dll_instance.externalunitinfos_destroy 
        self._externalunitinfos_destroy.restype = CAPIStatus
        self._externalunitinfos_destroy.argtypes = [POINTER(_ExternalUnitInfoVector)]

    def __del__(self):
        '''Destroys the handle individually by wrapping it in an
            external unit vector.
        '''
        
        vector = _ExternalUnitInfoVector(c_size_t(1), pointer(self._handle))
        self._externalunitinfos_destroy(byref(vector))

    @property
    def implant_type(self) -> str:
        '''Get the type of the connected implant.
        
            This property is read-only.
        '''

        buffer_size = 128
        buffer = create_string_buffer(buffer_size)
        string_length_ptr = c_size_t_ptr(c_size_t(0))
                
        status = self._externalunitinfo_getImplantType(self._handle, buffer, buffer_size, string_length_ptr)

        if status == CAPIStatus.STATUS_OK:
            return buffer.value.decode("utf-8")
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")

    
    @property
    def device_id(self) -> str:
        '''Get device identifier of the external unit.
        
            This property is read-only.
        '''

        buffer_size = 128
        buffer = create_string_buffer(buffer_size)
        string_length_ptr = c_size_t_ptr(c_size_t(0))
                
        status = self._externalunitinfo_getDeviceId(self._handle, buffer, buffer_size, string_length_ptr)

        if status == CAPIStatus.STATUS_OK:
            return buffer.value.decode("utf-8")
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")

    @property
    def firmware_version(self) -> str:
        '''Get firmware version of the external unit.
        
            This property is read-only.
        '''
        
        buffer_size = 128
        buffer = create_string_buffer(buffer_size)
        string_length_ptr = c_size_t_ptr(c_size_t(0))
                
        status = self._externalunitinfo_getFirmwareVersion(self._handle, buffer, buffer_size, string_length_ptr)

        if status == CAPIStatus.STATUS_OK:
            return buffer.value.decode("utf-8")
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")