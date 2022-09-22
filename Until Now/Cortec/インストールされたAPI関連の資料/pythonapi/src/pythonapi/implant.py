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
'''@doctring implant

    Generic implant class for all kinds of implants. This class acts as
    a facade to the hardware abstraction layer. Stimulation is
    triggered as an stimulation command, which is checked for compliance
    with the corresponding implant stimulation constraints and processed
    if it satisfies the requirements.

    All module functions return STATUS_RUNTIME_ERROR if the execution of
     the commands fails (e.g. missing connection).
'''

from ctypes import POINTER, pointer, byref, c_bool, c_uint32, c_size_t, c_double, Structure, create_string_buffer
from typing import List

from pythonapi.pythonapibase import get_api_base, CAPIStatus, _Opaque, opaque_ptr, _CAPIUint32Set, get_error_message, c_size_t_ptr
from pythonapi.implantlistener import _ImplantListener, ImplantListener
from pythonapi.implantinfo import ImplantInfo
from pythonapi.stimulationcommand import StimulationCommand

class Implant():
    '''Generic implant class for all kinds of implants.

       Create instances using the implant factory!
    '''

    def __init__(self, handle):
        api = get_api_base()
        self._handle = handle
        self.__registerMethods(api)

        self._listener = None

    def __registerMethods(self, api):
        '''Register DLL methods used by this class.'''
        
        self._implant_registerListener = api.dll_instance.implant_registerListener
        self._implant_registerListener.restype = CAPIStatus
        self._implant_registerListener.argtypes = [opaque_ptr, opaque_ptr]

        self._implant_unregisterListener = api.dll_instance.implant_unregisterListener
        self._implant_unregisterListener.restype = CAPIStatus
        self._implant_unregisterListener.argtypes = [opaque_ptr]

        self._implant_getImplantInfo = api.dll_instance.implant_getImplantInfo
        self._implant_getImplantInfo.restype = CAPIStatus
        self._implant_getImplantInfo.argtypes = [opaque_ptr, POINTER(opaque_ptr)]

        self._implant_startMeasurement = api.dll_instance.implant_startMeasurement
        self._implant_startMeasurement.restype = CAPIStatus
        self._implant_startMeasurement.argtypes = [opaque_ptr, _CAPIUint32Set]

        self._implant_stopMeasurement = api.dll_instance.implant_stopMeasurement
        self._implant_stopMeasurement.restype = CAPIStatus
        self._implant_stopMeasurement.argtypes = [opaque_ptr]

        self._implant_getImpedance = api.dll_instance.implant_getImpedance
        self._implant_getImpedance.restype = CAPIStatus
        self._implant_getImpedance.argtypes = [opaque_ptr, c_uint32, POINTER(c_double)]

        self._implant_getTemperature = api.dll_instance.implant_getTemperature
        self._implant_getTemperature.restype = CAPIStatus
        self._implant_getTemperature.argtypes = [opaque_ptr, POINTER(c_double)]

        self._implant_getHumidity = api.dll_instance.implant_getHumidity
        self._implant_getHumidity.restype = CAPIStatus
        self._implant_getHumidity.argtypes = [opaque_ptr, POINTER(c_double)]

        self._implant_isStimulationCommandValid = api.dll_instance.implant_isStimulationCommandValid
        self._implant_isStimulationCommandValid.restype = CAPIStatus

        self._implant_startStimulation = api.dll_instance.implant_startStimulation
        self._implant_startStimulation.restype = CAPIStatus
        self._implant_startStimulation.argtypes = [opaque_ptr, opaque_ptr]

        self._implant_stopStimulation = api.dll_instance.implant_stopStimulation
        self._implant_stopStimulation.restype = CAPIStatus
        self._implant_stopStimulation.argtypes = [opaque_ptr]

        self._implant_setImplantPower = api.dll_instance.implant_setImplantPower
        self._implant_setImplantPower.restype = CAPIStatus
        self._implant_setImplantPower.argtypes = [opaque_ptr, c_bool]

        self._implant_implant_pushState = api.dll_instance.implant_pushState
        self._implant_implant_pushState.restype = CAPIStatus
        self._implant_implant_pushState.argtypes = [opaque_ptr]

        self._implant_destroy = api.dll_instance.implant_destroy
        self._implant_destroy.restype = CAPIStatus
        self._implant_destroy.argtypes = [POINTER(opaque_ptr)]
        
    def __del__(self):
        self._implant_destroy(byref(self._handle))

    def register_listener(self, listener: ImplantListener):
        '''Register listener object, which is notified on arrival of 
            new data and errors. 
        
            The function needs to be called once before starting the
            measurement loop in order to receive measurement values. 
            On consecutive calls only the latest registered listener
            will be notified.

           @param listener (Type: ImplantListener) The listener 
                instance to be registered on the implant.
        '''
        new_listener = _ImplantListener(listener)
        status = self._implant_registerListener(self._handle, new_listener._handle)

        if status == CAPIStatus.STATUS_OK:
            self._listener = new_listener
        else:
            del new_listener
            raise RuntimeError(f"{status.name}: {get_error_message()}")

    def unregister_listener(self):
        '''Unregister listener object from an implant handle.'''

        status = self._implant_unregisterListener(self._handle)

        if status == CAPIStatus.STATUS_OK:
            self._listener = None
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")

    @property
    def implant_info(self) -> ImplantInfo:
        '''Get information about the implant.
        
            This property is read-only.
        '''

        implant_info = pointer(_Opaque())

        status = self._implant_getImplantInfo(self._handle, byref(implant_info))

        if status == CAPIStatus.STATUS_OK:
            return ImplantInfo(implant_info)
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")
    
    def start_measurement(self, ref_channels: List[int]):
        '''Starts measurement of data. Note that only the measurement
            result of the channels that are not used as reference 
            electrodes is valid. The measurement result for the 
            reference electrodes is the reference value.

           @param ref_channels (Type: List[int]) The list of reference 
                channels for the measurement.
        '''

        vector_size = len(ref_channels)
        # creates a custom type and converts ref_channels into it
        ctypes_vector = (c_uint32 * vector_size)(*ref_channels)
        ctypes_ref_channels = _CAPIUint32Set(c_size_t(vector_size), ctypes_vector)

        status = self._implant_startMeasurement(self._handle, ctypes_ref_channels)

        if status != CAPIStatus.STATUS_OK:
            raise RuntimeError(f"{status.name}: {get_error_message()}")
        
    def stop_measurement(self):
        '''Stops measurement of data.'''

        status = self._implant_stopMeasurement(self._handle)

        if status != CAPIStatus.STATUS_OK:
            raise RuntimeError(f"{status.name}: {get_error_message()}")

    def calculate_impedance(self, channel: int) -> float:
        '''Starts impedance measurement of one channel. This is a
            blocking call. Impedance measurement is only possible
            while no measurement or stimulation is running.

           @param ref_channels (Type: int) The channel number for 
                which the impedance should be measured. Starts at 0.
        '''

        impedance_value = c_double(0.)

        status = self._implant_getImpedance(self._handle, channel, impedance_value)

        if status == CAPIStatus.STATUS_OK:
            return impedance_value.value
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")

    @property
    def temperature(self) -> float:
        '''Measures the temperature within implant capsule. This is a
            blocking call. It will stop running measurements.
        
            This property is read-only.
        '''

        result = c_double(0.)

        status = self._implant_getTemperature(self._handle, byref(result))

        if status == CAPIStatus.STATUS_OK:
            return result.value
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")

    @property
    def humidity(self) -> float:
        '''Measures the humidity within implant capsule. This is a 
            blocking call. It will stop running measurements.
        
            This property is read-only.
        '''

        result = c_double(0.)

        status = self._implant_getHumidity(self._handle, byref(result))

        if status == CAPIStatus.STATUS_OK:
            return result.value
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")

    def is_stimulation_command_valid(self, command: StimulationCommand):
        '''Checks a stimulation command for validity, as if it would be used in startStimulation.
        
            @param[in] cmd The stimulation command to be checked
            
            @return true if the command is valid and false otherwise.
            @return An error message telling why the command is not valid. Equals the 
                                empty string if the command is valid.
        '''
        
        buffer_size = 256
        buffer = create_string_buffer(buffer_size)
        string_length_ptr = c_size_t_ptr(c_size_t(0))
        result = c_bool(False)

        status = self._implant_isStimulationCommandValid(self._handle, command._handle, byref(result), buffer, buffer_size, string_length_ptr)

        if status == CAPIStatus.STATUS_OK:
            return result.value, buffer.value.decode("utf-8")
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")

    def start_stimulation(self, command: StimulationCommand):
        '''Starts a stimulation. This is a non-blocking call (i.e. the
            call will schedule the stimulation but not wait until it is
            finished).

           @param command (Type: StimulationCommand) The command that
            should be stimulated.
        '''

        status = self._implant_startStimulation(self._handle, command._handle)

        if status == CAPIStatus.STATUS_OK:
            command.valid = False
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")
        
    def stop_stimulation(self):
        '''Stops stimulation.'''

        status = self._implant_stopStimulation(self._handle)

        if status != CAPIStatus.STATUS_OK:
            raise RuntimeError(f"{status.name}: {get_error_message()}")

    def set_implant_power(self, enabled: bool):
        '''Enable or disable power transfer to the implant (enabled
            by default). Note that powering on the implant takes some 
            milliseconds before it is responsive.

           @param enabled (Type: bool) The active state of the implant 
                power. True corresponds to power enabled.
        '''

        status = self._implant_setImplantPower(self._handle, c_bool(enabled))

        if status != CAPIStatus.STATUS_OK:
            raise RuntimeError(f"{status.name}: {get_error_message()}")

    def push_state(self):
        '''Tells the implant to propagate the current measurement and
            stimulation states through the registered listener. 
           
            This method can be used to synchronize GUIs with the
            implant's state. 
           
            Usage:
            1. register listener
            2. call pushState()
            3. update GUI based on callback from listener 
                (onMeasurementStateChanged()/onStimulationStateChanged())
        '''

        status = self._implant_implant_pushState(self._handle)

        if status != CAPIStatus.STATUS_OK:
            raise RuntimeError(f"{status.name}: {get_error_message()}")