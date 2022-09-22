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
'''@doctring channelinfo

    This module contains the datatypes used to retrieve information
    about individual channels.
'''
from ctypes import Structure, c_size_t, c_bool, c_double, POINTER, byref, c_int

from pythonapi.pythonapibase import _CAPIEnum, opaque_ptr, get_api_base, CAPIStatus, get_error_message

class UnitType(_CAPIEnum):
    '''Enumeration for unit types.'''

    UT_NO_UNIT = 0
    UT_CURRENT = 1
    UT_VOLTAGE = 2
    UT_COUNT   = 3

class _ChannelInfoVector(Structure):
    '''Vector of channel information.
  
        Each entry provides information on the specific electrode
        channel.
    '''

    _fields_ = [("count", c_size_t), 
                ("vector", POINTER(opaque_ptr))]

class ChannelInfo():
    '''Information on a single channel of an electrode.
    
        Use ImplantInfo to create instances!
    '''
    
    def __init__(self, handle):
        self._handle = handle

        api = get_api_base()
        self.__registerMethods(api)

    def __registerMethods(self, api):
        '''Register DLL methods used by this class.'''

        self._channelinfo_canMeasure = api.dll_instance.channelinfo_canMeasure
        self._channelinfo_canMeasure.restype = CAPIStatus
        self._channelinfo_canMeasure.argtypes = [opaque_ptr, POINTER(c_bool)]
        
        self._channelinfo_getMeasureValueMin = api.dll_instance.channelinfo_getMeasureValueMin
        self._channelinfo_getMeasureValueMin.restype = CAPIStatus
        self._channelinfo_getMeasureValueMin.argtypes = [opaque_ptr, POINTER(c_double)]
        
        self._channelinfo_getMeasureValueMax = api.dll_instance.channelinfo_getMeasureValueMax
        self._channelinfo_getMeasureValueMax.restype = CAPIStatus
        self._channelinfo_getMeasureValueMax.argtypes = [opaque_ptr, POINTER(c_double)]

        self._channelinfo_canStimulate = api.dll_instance.channelinfo_canStimulate
        self._channelinfo_canStimulate.restype = CAPIStatus
        self._channelinfo_canStimulate.argtypes = [opaque_ptr, POINTER(c_bool)]
        
        self._channelinfo_getStimulationUnit = api.dll_instance.channelinfo_getStimulationUnit
        self._channelinfo_getStimulationUnit.restype = CAPIStatus
        self._channelinfo_getStimulationUnit.argtypes = [opaque_ptr, POINTER(c_int)]

        self._channelinfo_getStimValueMin = api.dll_instance.channelinfo_getStimValueMin
        self._channelinfo_getStimValueMin.restype = CAPIStatus
        self._channelinfo_getStimValueMin.argtypes = [opaque_ptr, POINTER(c_double)]
        
        self._channelinfo_getStimValueMax = api.dll_instance.channelinfo_getStimValueMax
        self._channelinfo_getStimValueMax.restype = CAPIStatus
        self._channelinfo_getStimValueMax.argtypes = [opaque_ptr, POINTER(c_double)]

        self._channelinfo_canMeasureImpedance = api.dll_instance.channelinfo_canMeasureImpedance
        self._channelinfo_canMeasureImpedance.restype = CAPIStatus
        self._channelinfo_canMeasureImpedance.argtypes = [opaque_ptr, POINTER(c_bool)]

    @property
    def can_measure(self) -> bool:
        '''Check if the electrode is capable of measuring electrical
            signals.
        
            This property is read-only.
        '''
        
        result = c_bool(False)
        
        status = self._channelinfo_canMeasure(self._handle, byref(result))

        if status == CAPIStatus.STATUS_OK:
            return result.value
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")

    @property
    def measure_value_min(self) -> float:
        '''Get the minimum value in voltage [V] the electrode can
            measure.
        
            This property is read-only.
        '''
        
        result = c_double(False)
        
        status = self._channelinfo_getMeasureValueMin(self._handle, byref(result))

        if status == CAPIStatus.STATUS_OK:
            return result.value
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")

    @property
    def measure_value_max(self) -> float:
        '''Get the maximum value in voltage [V] the electrode can
            measure.
        
            This property is read-only.
        '''
        
        result = c_double(False)
        
        status = self._channelinfo_getMeasureValueMax(self._handle, byref(result))

        if status == CAPIStatus.STATUS_OK:
            return result.value
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")

    @property
    def can_measure_impedance(self) -> bool:
        '''Check if the electrode is capable of measuring its 
            impedance.
        
            This property is read-only.
        '''
        
        result = c_bool(False)
        
        status = self._channelinfo_canMeasureImpedance(self._handle, byref(result))

        if status == CAPIStatus.STATUS_OK:
            return result.value
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")

    @property
    def can_stimulate(self) -> bool:
        '''Check if the electrode is capable of stimulation.
        
            This property is read-only.
        '''

        result = c_bool(False)
        
        status = self._channelinfo_canStimulate(self._handle, byref(result))

        if status == CAPIStatus.STATUS_OK:
            return result.value
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")

    @property
    def stimulation_unit(self) -> UnitType:
        '''Get the unit type of the stimulation value.
        
            This property is read-only.
        '''
        
        result = c_int(UnitType.UT_NO_UNIT)
        
        status = self._channelinfo_getStimulationUnit(self._handle, byref(result))

        if status == CAPIStatus.STATUS_OK:
            return UnitType(result.value)
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")

    @property
    def stimulation_value_min(self) -> float:
        '''Get the minimum value in UnitType the electrode can emit
            for stimulation.
        
            The unit type can be accessed by calling get_stimulation_unit().
        
            This property is read-only.
        '''
                
        result = c_double(False)
        
        status = self._channelinfo_getStimValueMin(self._handle, byref(result))

        if status == CAPIStatus.STATUS_OK:
            return result.value
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")

    @property
    def stimulation_value_max(self) -> float:
        '''Get the maximum value in UnitType the electrode can emit for
            stimulation.
        
            The unit type can be accessed by calling get_stimulation_unit().
        
            This property is read-only.
        '''
        
        result = c_double(False)
        
        status = self._channelinfo_getStimValueMax(self._handle, byref(result))

        if status == CAPIStatus.STATUS_OK:
            return result.value
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")
