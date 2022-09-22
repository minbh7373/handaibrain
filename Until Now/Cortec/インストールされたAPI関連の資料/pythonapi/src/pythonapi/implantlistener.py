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
from ctypes import CFUNCTYPE, Structure, c_bool, c_double, c_char_p, c_uint16, c_uint32, c_uint64, c_int, POINTER, pointer, byref
from abc import ABCMeta, abstractmethod
from typing import List

from pythonapi.pythonapibase import _Opaque, opaque_ptr, get_api_base, CAPIStatus, _CAPIEnum

class Sample():
    '''Measurement data read by the implant at one point in time,
        i.e. for one sample.

        An instance holds the following information:

        - Number of channels used for measuring. Array measurements
            must be of this size.
        - Array of measurements. This array must be of size
            numberOfMeasurements.
        - Supply voltage in mV.
        - Information whether the implant is connected
            (all channels available).
        - Id of the stimulation which starts with this sample. If no
            stimulation started with this sample, then the
            stimulationNumber is IMPLANT_NO_STIMULATION.
        - Information whether the stimulation is active.
        - Counter that is increased for each measurement sample starting with 0.
            The value range is [0, 4294967295] (i.e. 2^32 - 1). If the maximum
            value is exceeded the counter will be reset automatically.
    '''
    def __init__(self, num_measurements: int, measurements: List[float], supply_voltage_mV: int, \
                 is_connected: bool, stimulation_id: int, is_stimulation_active: bool, measurement_counter: int):
        self.num_measurements = num_measurements
        self.measurements = measurements
        self.supply_voltage_mV = supply_voltage_mV
        self.is_connected = is_connected
        self.stimulation_id = stimulation_id
        self.is_stimulation_active = is_stimulation_active
        self.measurement_counter = measurement_counter

class _CtypesSample(Structure):
    '''Ctypes representation of the sample object.'''

    _fields_ = [("numberOfMeasurements", c_uint16), 
                ("measurements",         POINTER(c_double)),
                ("supplyVoltageMilliV",  c_uint32),
                ("isConnected",          c_bool),
                ("stimulationId",        c_uint16),
                ("isStimulationActive",  c_bool),
                ("measurementCounter",   c_uint32)]

class ConnectionType(_CAPIEnum):
    ''' Enumeration for different connections. 

        Note that not all implants have all connection types.
    
        Must always be synchronized with the respective C enum!
    '''

    CON_TYPE_EXT_TO_IMPLANT = 0
    CON_TYPE_PC_TO_EXT = 1
    CON_TYPE_UNKNOWN = 2
    
class ConnectionState(_CAPIEnum):
    '''Enumeration for the state of a connection, e.g., connected or
        disconnected. 
    
        Must always be synchronized with the respective C enum!
    '''

    CON_STATE_DISCONNECTED = 0
    CON_STATE_CONNECTED = 1
    CON_STATE_UNKNOWN = 2

_boolFunc_t  = CFUNCTYPE(None, c_bool)
_floatFunc_t = CFUNCTYPE(None, c_double)
_uint64Func_t = CFUNCTYPE(None, c_uint64)
_connectFunc_t = CFUNCTYPE(None, c_int, c_int) # ctypes does not accept using enums directly

class _CTypesImplantListener(Structure):
    '''Ctypes representation of the implant listener object.'''

    _fields_ = [
        ("onStimulationStateChanged",     _boolFunc_t),
        ("onMeasurementStateChanged",     _boolFunc_t),
        ("onConnectionStateChanged",      _connectFunc_t),
        ("onData",                        CFUNCTYPE(None, POINTER(_CtypesSample))),
        ("onImplantVoltageChanged",       _floatFunc_t),
        ("onPrimaryCoilCurrentChanged",   _floatFunc_t),
        ("onImplantControlValueChanged",  _floatFunc_t),
        ("onTemperatureChanged",          _floatFunc_t),
        ("onHumidityChanged",             _floatFunc_t),
        ("onError",                       CFUNCTYPE(None, c_char_p)),
        ("onDataProcessingTooSlow",       CFUNCTYPE(None)),
        ("onStimulationFunctionFinished", _uint64Func_t)
    ]


class ImplantListener(metaclass=ABCMeta):
    '''Class holding callback functions which are called by the implant
        to notify the user on certain events.
    
        For example, new measurement data, implant state changes or
        implant health state changes from an implant. It is possible to
        initialize single handles as NULL before creating the listener
        handle in order to not receive any events of a certain type. If
        the callbacks are not NULL they must point to callable
        functions!
        
        Please note that ignoring the onError event is not advisible for 
        medical devices, since error conditions could be lost.
    '''

    @abstractmethod
    def on_stimulation_state_changed(self, is_stimulating: bool):
        '''Callback receiving stimulation state changes.

           @param is_stimulating (Type: bool) Indicator whether the 
                stimulation is active. True corresponds to a running stimulation.
        '''
        raise NotImplementedError
    
    @abstractmethod
    def on_measurement_state_changed(self, is_measuring: bool):
        '''Callback receiving measurement state changes.

           @param is_measuring (Type: bool) Indicator whether the 
                stimulation is active. True corresponds to a running measurement.
        '''
        raise NotImplementedError
    
    @abstractmethod
    def on_connection_state_changed(self, connection_type: ConnectionType, connection_state: ConnectionState):
        '''Callback receiving connection state changes.

           @param connection_type  (Type: ConnectionType)  Information
                about the connection type.
           @param connection_state (Type: ConnectionState) Information
                about the connection state.
        '''
        raise NotImplementedError
    
    @abstractmethod
    def on_data(self, sample: Sample):
        '''Callback receiving measurement data.

           Important: Once the callback returns the pointed sample is
           no longer valid!

           @param sample (Type: Sample) One measurement sample.
        '''
        raise NotImplementedError
    
    @abstractmethod
    def on_implant_voltage_changed(self, voltage_V: float):
        '''Callback if a new supply voltage information was received
            from the implant.

           @param voltage_V (Type: float) The impant voltage in volts.
        '''
        raise NotImplementedError
    
    @abstractmethod
    def on_primary_coil_current_changed(self, current_mA: float):
        '''Callback if a new primary coil current value was received
            from the implant.

           @param current_mA (Type: float) The primary coil current
                value in Milliampere.
        '''
        raise NotImplementedError
    
    @abstractmethod
    def on_implant_control_value_changed(self, control_value: float):
        '''Callback if implant control value change was received from
            the external unit.

           @param control_value (Type: float) The implant control
                value.
        '''
        raise NotImplementedError
    
    @abstractmethod
    def on_temperature_changed(self, temperature: float):
        '''Callback if a new temperature information was received
            from the implant.
        
            Temperature of implant is in degree Celsius.

           @param temperature (Type: float) The temperature value.
        '''
        raise NotImplementedError
    
    @abstractmethod
    def on_humidity_changed(self, humidity: float):
        '''Callback if a new humidity information was received from
            the implant.
        
            Relative humidity of implant is given in percent.

           @param humidity (Type: float) The humidity value.
        '''
        raise NotImplementedError
    
    @abstractmethod
    def on_error(self, error_description: str):
        '''Callback for errors in driver library during measurement and
            stimulation.

            Examples:
            - Humidity exceeds safety limit and leads to critical 
                shutdown of the implant
            - Stimulation current exceeds safety limits potentially due
                to electrical malfunctions

            Important: Once the callback returns, the errorDescription 
                is no longer valid!

           @param error_description (Type: str) The message of the error.
        '''
        raise NotImplementedError
    
    @abstractmethod
    def on_data_processing_too_slow(self):
        '''Callback when onData calls are processed too slow.'''
        raise NotImplementedError
    
    @abstractmethod
    def on_stimulation_function_finished(self, num_executed_functions: int):
        '''Callback triggered during an active stimulation, if a stimulation function or pause was executed.
        
            @param[in] numFinishedFunctions (Type: number) The number of so far executed functions/pauses of the current command.
        '''
        raise NotImplementedError

class _ImplantListener():
    def __init__(self, listener: ImplantListener):
        api = get_api_base()

        implant_createListener = api.dll_instance.implant_createListener
        implant_createListener.restype = CAPIStatus
        implant_createListener.argtypes = [POINTER(_CTypesImplantListener), POINTER(opaque_ptr)]

        self._implant_destroyListener = api.dll_instance.implant_destroyListener
        self._implant_destroyListener.restype = CAPIStatus
        self._implant_destroyListener.argtypes = [POINTER(opaque_ptr)]

        self._handle = pointer(_Opaque())
        self._py_listener = listener
        self._ctypes_listener = self.connect_listener_methods()

        status = implant_createListener(byref(self._ctypes_listener), byref(self._handle))

        if status != CAPIStatus.STATUS_OK:
            self._handle = None
            raise RuntimeError(f"{status.name}: {api.error_message}")

    def __del__(self):
        if self._handle is not None:
            self._implant_destroyListener(byref(self._handle))

    def connect_listener_methods(self):
        '''Create bridge methods between the ctypes and the 
            python listener object.
        '''

        def onStimulationStateChanged(isStimulating: bool):
            self._py_listener.on_stimulation_state_changed(isStimulating)

        def onMeasurementStateChanged(isMeasuring: bool):
            self._py_listener.on_measurement_state_changed(isMeasuring)

        def onConnectionStateChanged(connectionType: int, connectionState: int):
            self._py_listener.on_connection_state_changed( \
                ConnectionType(connectionType), ConnectionState(connectionState))

        def onData(sample: POINTER(_CtypesSample)):
            c_sample = sample.contents
            measurements = c_sample.measurements[:c_sample.numberOfMeasurements]

            py_sample = Sample(c_sample.numberOfMeasurements, 
                                measurements,
                                c_sample.supplyVoltageMilliV,
                                c_sample.isConnected,
                                c_sample.stimulationId,
                                c_sample.isStimulationActive,
                                c_sample.measurementCounter)

            self._py_listener.on_data(py_sample)

        def onImplantVoltageChanged(voltageV: float):
            self._py_listener.on_implant_voltage_changed(voltageV)

        def onPrimaryCoilCurrentChanged(currentMilliA: float):
            self._py_listener.on_primary_coil_current_changed(currentMilliA)

        def onImplantControlValueChanged(controlValue: float):
            self._py_listener.on_implant_control_value_changed(controlValue)

        def onTemperatureChanged(temperature: float):
            self._py_listener.on_temperature_changed(temperature)

        def onHumidityChanged(humidity: float):
            self._py_listener.on_humidity_changed(humidity)

        def onError(errorDescription: bytes):
            self._py_listener.on_error(errorDescription.decode('utf-8'))

        def onDataProcessingTooSlow():
            self._py_listener.on_data_processing_too_slow()

        def onStimulationFunctionFinished(numExecutedFunctions: int):
            self._py_listener.on_stimulation_function_finished(numExecutedFunctions)

        return _CTypesImplantListener(
            _boolFunc_t(onStimulationStateChanged),
            _boolFunc_t(onMeasurementStateChanged),
            _connectFunc_t(onConnectionStateChanged),
            CFUNCTYPE(None, POINTER(_CtypesSample))(onData),
            _floatFunc_t(onImplantVoltageChanged),
            _floatFunc_t(onPrimaryCoilCurrentChanged),
            _floatFunc_t(onImplantControlValueChanged),
            _floatFunc_t(onTemperatureChanged),
            _floatFunc_t(onHumidityChanged),
            CFUNCTYPE(None, c_char_p)(onError),
            CFUNCTYPE(None)(onDataProcessingTooSlow),
            _uint64Func_t(onStimulationFunctionFinished)
        )