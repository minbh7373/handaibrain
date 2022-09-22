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

    This module defines classes for atomic elements of a stimulation 
    function.

    Each atom has a duration which is defined in micros and a type 
    (atom_type_t) that determines its form. Atoms can be appended to a
    stimulation function to define the function's signal form over 
    time.
'''
from ctypes import POINTER, byref, pointer, c_uint64, c_bool, c_int

from pythonapi.pythonapibase import _CAPIEnum, CAPIStatus, opaque_ptr, _Opaque, get_api_base, get_error_message

class AtomType(_CAPIEnum):
    '''Enumeration with all available stimulation atom types.'''

    AT_NOTYPE                  = 0
    AT_RECTANGULAR             = 1
    AT_RECTANGULAR_4_AMPLITUDE = 2
    AT_PAUSE                   = 3
    AT_UNSUPPORTED             = 4
    AT_COUNT                   = 5

class StimulationAtom():
    '''Atomic element of a stimulation function.'''

    def __init__(self, handle):
        self._handle = handle
        self.valid = True

        api = get_api_base()
        self.__registerMethods(api)

    def __registerMethods(self, api):
        '''Register DLL methods used by this class.'''

        self._stimulationatom_getDuration = api.dll_instance.stimulationatom_getDuration
        self._stimulationatom_getDuration.restype = CAPIStatus
        self._stimulationatom_getDuration.argtypes = [opaque_ptr, POINTER(c_uint64)]

        self._stimulationatom_getType = api.dll_instance.stimulationatom_getType
        self._stimulationatom_getType.restype = CAPIStatus
        self._stimulationatom_getType.argtypes = [opaque_ptr, POINTER(c_int)]

        self._stimulationatom_clone = api.dll_instance.stimulationatom_clone
        self._stimulationatom_clone.restype = CAPIStatus
        self._stimulationatom_clone.argtypes = [opaque_ptr, POINTER(opaque_ptr)]

        self._stimulationatom_isEqual = api.dll_instance.stimulationatom_isEqual
        self._stimulationatom_isEqual.restype = CAPIStatus
        self._stimulationatom_isEqual.argtypes = [opaque_ptr, opaque_ptr, POINTER(c_bool)]

        self._stimulationatom_destroy = api.dll_instance.stimulationatom_destroy
        self._stimulationatom_destroy.restype = CAPIStatus
        self._stimulationatom_destroy.argtypes = [POINTER(opaque_ptr)]

    def __del__(self):
        '''Destroy the stimulation atom handle if it was not
            invalidated by appending it to a function.
        '''
        if self.valid:
            self._stimulationatom_destroy(byref(self._handle))

    def __eq__(self, other):
        '''Compare two stimulation atoms.

           @param other (Type: StimulationAtom) The atom to be
                compared to.
        '''

        result = c_bool(False)
        
        status = self._stimulationatom_isEqual(self._handle, other._handle, byref(result))

        if status == CAPIStatus.STATUS_OK:
            return result.value
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")

    def __ne__(self, other):
        '''Compare two stimulation atoms.

           @param other (Type: StimulationAtom) The atom to be 
                compared to.
        '''

        return not self.__eq__(other)

    def __copy__(self):
        '''Create a shallow copy of the atom.'''

        copy = type(self)(self._handle)
        copy.valid = self.valid
        return copy

    def __deepcopy__(self, memo):
        '''Create a deep copy of the atom.

           @param memo Extra parameter of the python __deepcopy__
                function.
        '''

        copied_handle = pointer(_Opaque())

        status = self._stimulationatom_clone(self._handle, byref(copied_handle))

        if status == CAPIStatus.STATUS_OK:
            copy = type(self)(copied_handle)
            copy.valid = self.valid
            return copy
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")

    @property
    def duration(self) -> int:
        '''Get the duration of a stimulation atom.
        
            This property is read-only.
        '''

        result = c_uint64(0)
        
        status = self._stimulationatom_getDuration(self._handle, byref(result))

        if status == CAPIStatus.STATUS_OK:
            return result.value
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")

    @property
    def atom_type(self) -> AtomType:
        '''Get the type of a stimulation atom.
        
            This property is read-only.
        '''

        result = c_int(AtomType.AT_NOTYPE)
        
        status = self._stimulationatom_getType(self._handle, byref(result))

        if status == CAPIStatus.STATUS_OK:
            return AtomType(result.value)
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")