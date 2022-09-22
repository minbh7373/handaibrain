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
'''@doctring stimulationcommandfactory

    Factory interface for creation of stimulation commands, functions
    and atoms.

    Typical usage:
    1. Create empty stimulation command.
    2. Create empty stimulation function. Set repetition parameter.
    3. Create stimulation atoms and append them to function.
    4. Append stimulation function to command.
    5. Repeat steps 2. - 4. until all functions are created.
'''

from ctypes import pointer, byref, POINTER, c_double, c_uint64

from pythonapi.pythonapibase import get_api_base, CAPIStatus, _Opaque, opaque_ptr, get_error_message
from pythonapi.stimulationcommand import StimulationCommand
from pythonapi.stimulationfunction import StimulationFunction
from pythonapi.stimulationatom import StimulationAtom

class StimulationCommandFactory():
    '''Factory class for creating stimulation-related object instances.'''

    def __init__(self):
        api = get_api_base()

        stimulationcommandfactory_getFactoryHandle = \
            api.dll_instance.stimulationcommandfactory_getFactoryHandle
        stimulationcommandfactory_getFactoryHandle.restype = CAPIStatus
        stimulationcommandfactory_getFactoryHandle.argtypes = [POINTER(opaque_ptr)]

        self._handle = pointer(_Opaque())

        status = stimulationcommandfactory_getFactoryHandle(byref(self._handle))

        if status != CAPIStatus.STATUS_OK:
            raise RuntimeError(f"Could not create an stimulation command factory due to error: {status.name}")

        self.__registerMethods(api)

    def __registerMethods(self, api):
        '''Register DLL methods used by this class.'''
        
        self._stimulationcommandfactory_createStimulationCommand = \
             api.dll_instance.stimulationcommandfactory_createStimulationCommand
        self._stimulationcommandfactory_createStimulationCommand.restype = CAPIStatus
        self._stimulationcommandfactory_createStimulationCommand.argtypes = [opaque_ptr, POINTER(opaque_ptr)]
                
        self._stimulationcommandfactory_createStimulationFunction = \
             api.dll_instance.stimulationcommandfactory_createStimulationFunction
        self._stimulationcommandfactory_createStimulationFunction.restype = CAPIStatus
        self._stimulationcommandfactory_createStimulationFunction.argtypes = [opaque_ptr, POINTER(opaque_ptr)]

        self._stimulationcommandfactory_createRectStimulationAtom = \
            api.dll_instance.stimulationcommandfactory_createRectStimulationAtom
        self._stimulationcommandfactory_createRectStimulationAtom.restype = CAPIStatus
        self._stimulationcommandfactory_createRectStimulationAtom.argtypes = \
            [opaque_ptr, POINTER(opaque_ptr), c_double, c_uint64]

        self._stimulationcommandfactory_create4RectStimulationAtom = \
            api.dll_instance.stimulationcommandfactory_create4RectStimulationAtom
        self._stimulationcommandfactory_create4RectStimulationAtom.restype = CAPIStatus
        self._stimulationcommandfactory_create4RectStimulationAtom.argtypes = \
            [opaque_ptr, POINTER(opaque_ptr), c_double, c_double, c_double, c_double, c_uint64]
            
        self._stimulationcommandfactory_createStimulationPauseAtom = \
            api.dll_instance.stimulationcommandfactory_createStimulationPauseAtom
        self._stimulationcommandfactory_createStimulationPauseAtom.restype = CAPIStatus
        self._stimulationcommandfactory_createStimulationPauseAtom.argtypes = \
            [opaque_ptr, POINTER(opaque_ptr), c_uint64]

    def create_stimulation_command(self):
        '''Creates an empty stimulation command.'''

        command = pointer(_Opaque())

        status = self._stimulationcommandfactory_createStimulationCommand(self._handle, byref(command))

        if status == CAPIStatus.STATUS_OK:
            return StimulationCommand(command)
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")

    def create_stimulation_function(self):
        '''Creates an empty stimulation function.'''

        function = pointer(_Opaque())

        status = self._stimulationcommandfactory_createStimulationFunction(self._handle, byref(function))

        if status == CAPIStatus.STATUS_OK:
            return StimulationFunction(function)
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")

    def create_rect_stimulation_atom(self, value: float, duration: int):
        '''Creates a stimulation atom. Each atom represents a constant
            amplitude for a fixed time duration.

            Example: Using createRectStimulationAtom(12, 2000000) would
            return a stimulation atom that stimulates with 12 micro ampere
            for 2 seconds.

           @param value    (Type: float) The amplitude of the 
                stimulation in uA.
           @param duration (Type: int)   The atom duration in us.
        '''

        atom = pointer(_Opaque())

        status = self._stimulationcommandfactory_createRectStimulationAtom( \
            self._handle, byref(atom), c_double(value), c_uint64(duration))

        if status == CAPIStatus.STATUS_OK:
            return StimulationAtom(atom)
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")

    def create_4rect_stimulation_atom(self, amplitude0: float, amplitude1: float,
                            amplitude2: float, amplitude3: float, duration: int):
        '''Creates a stimulation atom with four different amplitudes.
            Each atom represents four constant amplitudes for a fixed
            time duration.

           @param amplitude0 (Type: float) The amplitude1 of the 
                stimulation in uA.
           @param amplitude1 (Type: float) The amplitude2 of the 
                stimulation in uA.
           @param amplitude2 (Type: float) The amplitude3 of the 
                stimulation in uA.
           @param amplitude3 (Type: float) The amplitude4 of the 
                stimulation in uA.
           @param duration   (Type: int)   The atom duration in us.
        '''

        atom = pointer(_Opaque())

        status = self._stimulationcommandfactory_create4RectStimulationAtom( \
            self._handle, byref(atom), c_double(amplitude0), \
            c_double(amplitude1), c_double(amplitude2), c_double(amplitude3), c_uint64(duration))

        if status == CAPIStatus.STATUS_OK:
            return StimulationAtom(atom)
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")

    def create_stimulation_pause_atom(self, duration: int):
        ''' Creates a stimulation pause atom with a given duration
            (no amplitudes).

           @param duration   (Type: int)   The pause duration in us.
        '''

        atom = pointer(_Opaque())

        status = self._stimulationcommandfactory_createStimulationPauseAtom( \
            self._handle, byref(atom), c_uint64(duration))

        if status == CAPIStatus.STATUS_OK:
            return StimulationAtom(atom)
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")
