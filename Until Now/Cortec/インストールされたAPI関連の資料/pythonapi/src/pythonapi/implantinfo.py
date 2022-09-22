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
'''@doctring implantinfo

    Information about the implant including channel info.
'''
from ctypes import create_string_buffer, c_size_t, pointer, byref, POINTER, c_uint32
from pythonapi.pythonapibase import get_api_base, CAPIStatus, c_size_t_ptr, opaque_ptr, _Opaque, get_error_message
from pythonapi.channelinfo import _ChannelInfoVector, ChannelInfo

class ImplantInfo():
    '''Class holding information about a connected implant.

        Create instances using the implant factory!
    '''

    def __init__(self, handle):
        self._handle = handle

        api = get_api_base()
        
        self._implantinfo_getFirmwareVersion = api.dll_instance.implantinfo_getFirmwareVersion
        self._implantinfo_getFirmwareVersion.restype = CAPIStatus

        self._implantinfo_getDeviceType = api.dll_instance.implantinfo_getDeviceType
        self._implantinfo_getDeviceType.restype = CAPIStatus

        self._implantinfo_getDeviceId = api.dll_instance.implantinfo_getDeviceId
        self._implantinfo_getDeviceId.restype = CAPIStatus

        self._implantinfo_getChannelInfo = api.dll_instance.implantinfo_getChannelInfo 
        self._implantinfo_getChannelInfo.restype = CAPIStatus
        self._implantinfo_getChannelInfo.argtypes = [opaque_ptr, POINTER(_ChannelInfoVector)]

        self._implantinfo_getChannelCount = api.dll_instance.implantinfo_getChannelCount 
        self._implantinfo_getChannelCount.restype = CAPIStatus
        self._implantinfo_getChannelCount.argtypes = [opaque_ptr, c_size_t_ptr]

        self._implantinfo_getMeasurementChannelCount = api.dll_instance.implantinfo_getMeasurementChannelCount 
        self._implantinfo_getMeasurementChannelCount.restype = CAPIStatus
        self._implantinfo_getMeasurementChannelCount.argtypes = [opaque_ptr, c_size_t_ptr]

        self._implantinfo_getStimulationChannelCount = api.dll_instance.implantinfo_getStimulationChannelCount 
        self._implantinfo_getStimulationChannelCount.restype = CAPIStatus
        self._implantinfo_getStimulationChannelCount.argtypes = [opaque_ptr, c_size_t_ptr]

        self._implantinfo_getSamplingRate = api.dll_instance.implantinfo_getSamplingRate 
        self._implantinfo_getSamplingRate.restype = CAPIStatus
        self._implantinfo_getSamplingRate.argtypes = [opaque_ptr, POINTER(c_uint32)]

        self._implantinfo_destroy = api.dll_instance.implantinfo_destroy 
        self._implantinfo_destroy.restype = CAPIStatus
        self._implantinfo_destroy.argtypes = [POINTER(opaque_ptr)]

    def __del__(self):
        if self._handle is not None:
            self._implantinfo_destroy(byref(self._handle))

    @property
    def firmware_version(self) -> str:
        '''Get firmware version of the implant.
        
            This property is read-only.
        '''

        buffer_size = 128
        buffer = create_string_buffer(buffer_size)
        string_length_ptr = c_size_t_ptr(c_size_t(0))
                
        status = self._implantinfo_getFirmwareVersion(self._handle, buffer, buffer_size, string_length_ptr)

        if status == CAPIStatus.STATUS_OK:
            return buffer.value.decode("utf-8")
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")

    @property
    def device_type(self) -> str:
        '''Get the type of the connected implant.
        
            This property is read-only.
        '''

        buffer_size = 128
        buffer = create_string_buffer(buffer_size)
        string_length_ptr = c_size_t_ptr(c_size_t(0))
                
        status = self._implantinfo_getDeviceType(self._handle, buffer, buffer_size, string_length_ptr)

        if status == CAPIStatus.STATUS_OK:
            return buffer.value.decode("utf-8")
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")
    
    @property
    def device_id(self) -> str:
        '''Get device identifier of the implant.
        
            This property is read-only.
        '''

        buffer_size = 128
        buffer = create_string_buffer(buffer_size)
        string_length_ptr = c_size_t_ptr(c_size_t(0))
                
        status = self._implantinfo_getDeviceId(self._handle, buffer, buffer_size, string_length_ptr)

        if status == CAPIStatus.STATUS_OK:
            return buffer.value.decode("utf-8")
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")
    
    @property
    def channel_info(self):
        '''Get information of the capabilities of each channel.
        
            This property is read-only.
        '''
        
        vector_size = 127
        vector_t = POINTER(_Opaque) * vector_size
        channel_info_vector = _ChannelInfoVector(c_size_t(vector_size), pointer(vector_t()[0]))

        status = self._implantinfo_getChannelInfo(self._handle, byref(channel_info_vector))

        if status == CAPIStatus.STATUS_OK:
            return self._convert_to_channel_infos(channel_info_vector)
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")

    def _convert_to_channel_infos(self, info_vector):
        '''Convert the C data structure to python objects'''

        if info_vector.count > 0:
            result = []
            for i in range(info_vector.count):
                channel_info = ChannelInfo(info_vector.vector[i])
                result.append(channel_info)
            return result
        else:
            return []
    
    @property
    def channel_count(self) -> int:
        '''Get the total number of channels.
        
            This property is read-only.
        '''
        
        channel_count = c_size_t(0)
                
        status = self._implantinfo_getChannelCount(self._handle, byref(channel_count))

        if status == CAPIStatus.STATUS_OK:
            return channel_count.value
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")
    
    @property
    def measurement_channel_count(self) -> int:
        '''Get the number of channels with measurement capabilities.
        
            This property is read-only.
        '''
                
        meas_channel_count = c_size_t(0)
                
        status = self._implantinfo_getMeasurementChannelCount(self._handle, byref(meas_channel_count))

        if status == CAPIStatus.STATUS_OK:
            return meas_channel_count.value
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")
    
    @property
    def stimulation_channel_count(self) -> int:
        '''Get the number of channels with stimulation capabilities.
        
            This property is read-only.
        '''
                        
        stim_channel_count = c_size_t(0)
                
        status = self._implantinfo_getStimulationChannelCount(self._handle, byref(stim_channel_count))

        if status == CAPIStatus.STATUS_OK:
            return stim_channel_count.value
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")
    
    @property
    def sampling_rate(self) -> int:
        '''Get the measurement sampling rate.
        
            This property is read-only.
        '''
                                
        sampling_rate = c_uint32(0)
                
        status = self._implantinfo_getSamplingRate(self._handle, byref(sampling_rate))

        if status == CAPIStatus.STATUS_OK:
            return sampling_rate.value
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")