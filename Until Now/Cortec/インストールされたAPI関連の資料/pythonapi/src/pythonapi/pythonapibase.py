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
''' @docstring pythonApi

    This module wraps the base functionality of the implantbic3232h 
    C api to be used with python.

    It offers a python definition of the c API status enum as well as
    helper classes to generate ctypes compatible enums. It is further 
    responsible for loading the DLL and offering it to other parts of 
    the API.
'''

from ctypes import CDLL, POINTER, create_string_buffer, c_size_t, Structure, c_uint32
from enum import IntEnum
from platform import architecture
import os

class _Opaque(Structure):
    pass

c_size_t_ptr = POINTER(c_size_t)
opaque_ptr = POINTER(_Opaque)

class _CAPIEnum(IntEnum):
    '''A ctypes-compatible IntEnum superclass.'''

    @classmethod
    def from_param(cls, object):
        ''' Converts a given value into an integer. Must be implemented
            to be used with ctypes.
        '''
        return int(object)

class CAPIStatus(_CAPIEnum):
    '''Python version of the C-API status enum. 
    
        Must always be synchronized with the respective C enum!
    '''

    STATUS_OK = 0
    STATUS_NULL_POINTER_ERROR = 1
    STATUS_RUNTIME_ERROR = 2
    STATUS_STRING_TOO_LONG = 3
    STATUS_VECTOR_TOO_LONG = 4
    STATUS_SET_TOO_BIG = 5
    STATUS_COUNT = 6

class _CAPIUint32Set(Structure):
    '''Ctype representing a set of uint32 integers.'''

    _fields_ = [("size", c_size_t), 
                ("elements", POINTER(c_uint32))]

class PythonAPIBase():
    '''Base class of the Cortec python API. 
    
        Gives information about the used library version. It is further
        responsible for accessing error information from the internal 
        (i.e. non-python) system components.
    '''

    def __init__(self, capi):
        self.dll_instance = capi

        self._capi_getLibraryVersion = capi.capi_getLibraryVersion
        self._capi_getLibraryVersion.restype = CAPIStatus

        self._capi_getErrorMessage = capi.capi_getErrorMessage
        self._capi_getErrorMessage.restype = CAPIStatus

    @property
    def library_version(self):
        '''Returns the used library version.'''

        buffer_size = 128
        buffer = create_string_buffer(buffer_size)
        string_length_ptr = c_size_t_ptr(c_size_t(0))

        status = self._capi_getLibraryVersion(buffer, buffer_size, string_length_ptr)

        if status == CAPIStatus.STATUS_OK:
            return buffer.value.decode("utf-8")
        else:
            raise RuntimeError(f"Could not retrieve library version due to error: {status.name}")

    @property
    def error_message(self):
        '''Returns message of internally occurred errors or empty string
            if no error has occurred.
        '''

        buffer_size = 512
        buffer = create_string_buffer(buffer_size)
        string_length_ptr = c_size_t_ptr(c_size_t(0))

        status = self._capi_getErrorMessage(buffer, buffer_size, string_length_ptr)

        if status == CAPIStatus.STATUS_OK:
            return buffer.value.decode("utf-8")
        else:
            raise RuntimeError(f"Could not retrieve error message due to error: {status.name}")

# Module-global to store the loaded dll in a single class 
_api_base: PythonAPIBase = None

def _load_dll():
    '''Load the C api dll.'''
    try:
        return CDLL('cimplantapi')
    except Exception as e:
        return _load_from_fallback_path()

def _load_from_fallback_path():
    '''Load dll from c api installation directoy relative to python
        api installation.

        Requires additional loading of all dlls the C api depends on.
    '''
    try:
        required_dlls = []
        dll_dir = _get_dll_dir()
        for dll_file in os.listdir(dll_dir):
            if dll_file.endswith('.dll') and 'cimplantapi' not in dll_file and not dll_file.endswith('D.dll'):
                required_dlls.append(CDLL(os.path.join(dll_dir, dll_file)))
        return CDLL(os.path.join(dll_dir, 'cimplantapi.dll'))
    except:
        raise RuntimeError("Cortec C-API could not be loaded.")

def _get_dll_dir():
    '''Returns the path to the C API installation depending on the used python
        interpreter version (32bit/64bit) based on a standard API installation
    '''
    if(architecture()[0] == "32bit"):
        return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'capi', 'lib32'))
    else:
        return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'capi', 'lib64'))

def get_api_base():
    '''Loads the implant c dll. Must be executed at least once before
        the api can be used.
    '''

    global _api_base
    if _api_base is None:
        main_dll = _load_dll()
        _api_base = PythonAPIBase(main_dll)
    return _api_base

def get_library_version():
    '''Retrieves and returns the current API version.'''

    api = get_api_base()
    return api.library_version
    
def get_error_message():
    '''Retrieves and returns the current API error message.'''

    api = get_api_base()
    return api.error_message
