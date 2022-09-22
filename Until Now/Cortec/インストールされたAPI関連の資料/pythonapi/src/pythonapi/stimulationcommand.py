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
'''@doctring stimulationcommand

    A stimulation command defines a sequence of stimulation functions,
    which are executed one after the other by the implant.
    
    This is a generic interface that is intended to be used with 
    different types of implants with different stimulation capabilities
    each. Stimulation capabilities may vary regarding the number of
    channels used for stimulation, stimulation amplitude, form of the
    stimulation signal over time. To reflect this, a stimulation 
    command consists of a sequence of stimulation functions. A 
    stimulation function can be composed arbitrarily complex.

    Each command holds a tracing id that can be set arbitrarily. This id is used to identify executions of the
    command in the application logs.
    
    The execution of a command can be executed internally by setting a number of repetitions > 1. This number of
    repetitions differs from the repetitions of stimulation functions, since all functions in the command are repeated.
    
    Example: Given a command that contains stimulation function A and B and a repetition number of 3. Then, the
    command functions will be executed as follows:
    
    A | B | A | B | A | B

    If for the function A, the repetition number is set to 2 additionally, the execution changes to:

    A | A | B | A | A | B | A | A | B
    
    Typical usage of a stimulation command:
    1. Create an empty stimulation command instance (with stimulation 
        command factory)
    2. Repeatedly add stimulationFunction instances
    3. Send stimulation command to implant by calling 
        implant_startStimulation().
'''

from ctypes import POINTER, byref, pointer, c_uint16, c_uint64, c_bool, c_size_t, create_string_buffer

from pythonapi.pythonapibase import get_api_base, CAPIStatus, opaque_ptr, _Opaque, c_size_t_ptr, get_error_message
from pythonapi.stimulationfunction import StimulationFunction

class _CommandIterator():
    '''Helper class for iterating over the functions in a stim command.
        Is unaware of wether it is repetition-aware or not.
    '''

    def __init__(self, handle):
        self._handle = handle
        
        api = get_api_base()
        self.__registerMethods(api)

    def __registerMethods(self, api):
        '''Register DLL methods used by this class.'''

        self._stimulationfunctioniterator_next = api.dll_instance.stimulationfunctioniterator_next
        self._stimulationfunctioniterator_next.restype = CAPIStatus
        self._stimulationfunctioniterator_next.argtypes = [opaque_ptr]
        
        self._stimulationfunctioniterator_isDone = api.dll_instance.stimulationfunctioniterator_isDone
        self._stimulationfunctioniterator_isDone.restype = CAPIStatus
        self._stimulationfunctioniterator_isDone.argtypes = [opaque_ptr, POINTER(c_bool)]

        self._stimulationfunctioniterator_getCurrentItem = api.dll_instance.stimulationfunctioniterator_getCurrentItem
        self._stimulationfunctioniterator_getCurrentItem.restype = CAPIStatus
        self._stimulationfunctioniterator_getCurrentItem.argtypes = [opaque_ptr, POINTER(opaque_ptr)]
        
        self._stimulationfunctioniterator_destroy = api.dll_instance.stimulationfunctioniterator_destroy
        self._stimulationfunctioniterator_destroy.restype = CAPIStatus
        self._stimulationfunctioniterator_destroy.argtypes = [POINTER(opaque_ptr)]

    def __del__(self):
        '''Destroy iterator handle.'''
        self._destroy_iterator_handle()   

    def __iter__(self):
        ''' Make this object iterable.'''

        return self

    def __next__(self):
        '''Get next stimulation function in iteration.'''

        if self._iterator_is_done():
            raise StopIteration
        else:
            function = self._get_current_item()
            status = self._stimulationfunctioniterator_next(self._handle)
            
            if status == CAPIStatus.STATUS_OK:
                return function
            else:
                raise RuntimeError(f"{status.name}: {get_error_message()}")

    def _get_current_item(self):
        '''Returns the current item or None if no iterator exists.'''
        
        function_handle = pointer(_Opaque())

        status = self._stimulationfunctioniterator_getCurrentItem(self._handle, byref(function_handle))
        
        if status == CAPIStatus.STATUS_OK:
            function = StimulationFunction(function_handle)
            function.valid = False
            return function
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")

    def _iterator_is_done(self):
        '''True if all elements of the container have been traversed.'''
        
        result = c_bool(False)

        status = self._stimulationfunctioniterator_isDone(self._handle, byref(result))
        
        if status == CAPIStatus.STATUS_OK:
            return result.value
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")
    
    def _destroy_iterator_handle(self):
        '''Destroy stimulation function iterator generated by
            self.__iter__.
        '''

        status = self._stimulationfunctioniterator_destroy(self._handle)

        if status != CAPIStatus.STATUS_OK:
            raise RuntimeError(f"{status.name}: {get_error_message()}")

class StimulationCommand():
    '''Class representation of a stimulation command.

        Functions in the command can be iterated in two ways:

        1) Individually     (i.e. 'for function in command:' or 
            'for function in command.iterator():' )
        2) Repetition-aware (i.e.  
            'for function in command.repetition_aware_iterator():')
    '''
    
    def __init__(self, handle):
        self._handle = handle
        self.valid = True

        self._api = get_api_base()
        self.__registerMethods(self._api)

    def __registerMethods(self, api):
        '''Register DLL methods used by this class.'''

        self._stimulationcommand_append = api.dll_instance.stimulationcommand_append
        self._stimulationcommand_append.restype = CAPIStatus
        self._stimulationcommand_append.argtypes = [opaque_ptr, POINTER(opaque_ptr)]
        
        self._stimulationcommand_getFunctionIterator = \
            api.dll_instance.stimulationcommand_getFunctionIterator
        self._stimulationcommand_getFunctionIterator.restype = CAPIStatus
        self._stimulationcommand_getFunctionIterator.argtypes = [opaque_ptr, POINTER(opaque_ptr)]
        
        self._stimulationcommand_getCommandRepetitionAwareFunctionIterator = \
             api.dll_instance.stimulationcommand_getCommandRepetitionAwareFunctionIterator
        self._stimulationcommand_getCommandRepetitionAwareFunctionIterator.restype = CAPIStatus
        self._stimulationcommand_getCommandRepetitionAwareFunctionIterator.argtypes = [opaque_ptr, POINTER(opaque_ptr)]
        
        self._stimulationcommand_getRepetitionAwareFunctionIterator = \
             api.dll_instance.stimulationcommand_getRepetitionAwareFunctionIterator
        self._stimulationcommand_getRepetitionAwareFunctionIterator.restype = CAPIStatus
        self._stimulationcommand_getRepetitionAwareFunctionIterator.argtypes = [opaque_ptr, POINTER(opaque_ptr)]

        self._stimulationcommand_getDuration = api.dll_instance.stimulationcommand_getDuration
        self._stimulationcommand_getDuration.restype = CAPIStatus
        self._stimulationcommand_getDuration.argtypes = [opaque_ptr, POINTER(c_uint64)]

        self._stimulationcommand_getName = api.dll_instance.stimulationcommand_getName
        self._stimulationcommand_getName.restype = CAPIStatus
        
        self._stimulationcommand_setName = api.dll_instance.stimulationcommand_setName
        self._stimulationcommand_setName.restype = CAPIStatus

        self._stimulationcommand_clone = api.dll_instance.stimulationcommand_clone
        self._stimulationcommand_clone.restype = CAPIStatus
        self._stimulationcommand_clone.argtypes = [opaque_ptr, POINTER(opaque_ptr)]

        self._stimulationcommand_getSize = api.dll_instance.stimulationcommand_getSize
        self._stimulationcommand_getSize.restype = CAPIStatus
        self._stimulationcommand_getSize.argtypes = [opaque_ptr, POINTER(c_uint64)]

        self._stimulationcommand_setTracingId = api.dll_instance.stimulationcommand_setTracingId
        self._stimulationcommand_setTracingId.restype = CAPIStatus
        self._stimulationcommand_setTracingId.argtypes = [opaque_ptr, c_uint16]

        self._stimulationcommand_getTracingId = api.dll_instance.stimulationcommand_getTracingId
        self._stimulationcommand_getTracingId.restype = CAPIStatus
        self._stimulationcommand_getTracingId.argtypes = [opaque_ptr, POINTER(c_uint16)]

        self._stimulationcommand_setRepetitions = api.dll_instance.stimulationcommand_setRepetitions
        self._stimulationcommand_setRepetitions.restype = CAPIStatus
        self._stimulationcommand_setRepetitions.argtypes = [opaque_ptr, c_uint16]

        self._stimulationcommand_getRepetitions = api.dll_instance.stimulationcommand_getRepetitions
        self._stimulationcommand_getRepetitions.restype = CAPIStatus
        self._stimulationcommand_getRepetitions.argtypes = [opaque_ptr, POINTER(c_uint16)]

        self._stimulationcommand_destroy = api.dll_instance.stimulationcommand_destroy
        self._stimulationcommand_destroy.restype = CAPIStatus
        self._stimulationcommand_destroy.argtypes = [POINTER(opaque_ptr)]
    
    def __del__(self):
        '''Destroy the stimulation command if it was not invalidated by
            running it on an implant.
        '''
        if self.valid:
            self._stimulationcommand_destroy(byref(self._handle))

    def __copy__(self):
        '''Create a shallow copy of the command.'''

        copy = type(self)(self._handle)
        copy.valid = self.valid
        return copy
    
    def __deepcopy__(self, memo):
        '''Make a deep copy of the stimulation command.

           @param memo Extra parameter of the python 
                __deepcopy__ function.
        '''

        copied_handle = pointer(_Opaque())

        status = self._stimulationcommand_clone(self._handle, byref(copied_handle))

        if status == CAPIStatus.STATUS_OK:
            copy = type(self)(copied_handle)
            copy.valid = self.valid
            return copy
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")

    def __iter__(self):
        '''Create an iterator that is not repetition aware.'''

        return self.iterator()

    def iterator(self):
        '''Create an iterator that is not repetition aware.'''

        iterator_handle = pointer(_Opaque())

        status = self._stimulationcommand_getFunctionIterator(self._handle, byref(iterator_handle))
        
        if status == CAPIStatus.STATUS_OK:
            return _CommandIterator(iterator_handle)
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")

    def repetition_aware_iterator(self):
        '''Create an iterator that is function repetition aware.'''

        iterator_handle = pointer(_Opaque())

        status = self._stimulationcommand_getRepetitionAwareFunctionIterator(self._handle, byref(iterator_handle))
        
        if status == CAPIStatus.STATUS_OK:
            return _CommandIterator(iterator_handle)
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")
        
    def command_repetition_aware_iterator(self):
        '''Create an iterator that is command repetition aware.'''

        iterator_handle = pointer(_Opaque())

        status = self._stimulationcommand_getCommandRepetitionAwareFunctionIterator(self._handle, byref(iterator_handle))
        
        if status == CAPIStatus.STATUS_OK:
            return _CommandIterator(iterator_handle)
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")

    def append(self, function: StimulationFunction):
        '''Append a stimulation function. The sequence of appends
            defines the sequence of execution.

            Invalidates the function object.

           @param function (Type: StimulationFunction) A stimulation 
                function to be appended.
        '''

        status = self._stimulationcommand_append(self._handle, byref(function._handle))

        if status == CAPIStatus.STATUS_OK:
            function.valid = False
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")

    @property
    def duration(self) -> int:
        '''Get the total duration of the stimulation command in
            microseconds. Is aware of command repetitions.
        
            This property is read-only.
        '''
                
        result = c_uint64(0)

        status = self._stimulationcommand_getDuration(self._handle, byref(result))
        
        if status == CAPIStatus.STATUS_OK:
            return result.value
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")

    @property
    def name(self) -> str:
        '''Get the name of the command. If the command name was not 
            set, empty string is returned'''

        buffer_size = 128
        buffer = create_string_buffer(buffer_size)
        string_length_ptr = c_size_t_ptr(c_size_t(0))
                
        status = self._stimulationcommand_getName(self._handle, buffer, buffer_size, string_length_ptr)

        if status == CAPIStatus.STATUS_OK:
            return buffer.value.decode("utf-8")
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")

    @name.setter
    def name(self, value: str):
        '''Set the name of the command.

           @param value (Type: str) The new name of the command.
        '''
                
        status = self._stimulationcommand_setName(self._handle, value.encode('utf-8'), len(value))

        if status != CAPIStatus.STATUS_OK:
            raise RuntimeError(f"{status.name}: {get_error_message()}")

    @property
    def size(self) -> int:
        '''Get the number of stimulation functions in the command. The given size is only aware of 
           command repetitions but not function repetitions.
        '''

        result = c_uint64(0)

        status = self._stimulationcommand_getSize(self._handle, byref(result))
        
        if status == CAPIStatus.STATUS_OK:
            return result.value
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")

    @property
    def tracing_id(self) -> int:
        '''Get the command's tracing id.'''

        result = c_uint16(0)
                
        status = self._stimulationcommand_getTracingId(self._handle, byref(result))

        if status == CAPIStatus.STATUS_OK:
            return result.value
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")

    @tracing_id.setter
    def tracing_id(self, value: int):
        '''Set the command's tracing id.

           @param value (Type: int) The new tracing id of the command.
        '''
                
        status = self._stimulationcommand_setTracingId(self._handle, c_uint16(value))

        if status != CAPIStatus.STATUS_OK:
            raise RuntimeError(f"{status.name}: {get_error_message()}")

    @property
    def repetitions(self) -> int:
        '''Get the command's repetitions.'''

        result = c_uint16(0)
                
        status = self._stimulationcommand_getRepetitions(self._handle, byref(result))

        if status == CAPIStatus.STATUS_OK:
            return result.value
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")

    @repetitions.setter
    def repetitions(self, value: int):
        '''Set the command's repetitions.

           @param value (Type: int) The new repetitions of the command.
        '''
                
        status = self._stimulationcommand_setRepetitions(self._handle, c_uint16(value))

        if status != CAPIStatus.STATUS_OK:
            raise RuntimeError(f"{status.name}: {get_error_message()}")
