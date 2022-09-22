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
'''@doctring stimulationfunction

    A stimulation function defines what stimulation signal is applied
    to which electrodes.
  
    A stimulation function consists of
    - a sequence of stimulation atoms that can be repeated a number of
        times
    - and the information which electrodes to use for stimulation.

    There are two types of stimulation that consist of the following atoms:

    1) A stimulation pause: one pause atom
    2) A stimulation pulse: five 4-rect stimulation atoms
      
    The stimulation atoms in the second case each describe one specific part
    of the stimulation pulse, including main and counter pulses as well
    as dead zones between them. The five stimulation atoms form a stimulation
    cove of the form:
                     ____
    Pulse      _   _|    |_ _____
                | |
                |_|
    
    Atom         1 2   3  4   5
    
    Pulse Atom Definition:
    
    1) Main pulse:    Holds the amplitude and duration of the main pulse
                      in uA and us. The acceptable value range goes from
                      -6120 to 0 uA. 
                      The granularity changes for smaller amplitudes as follows:
                        amplitude >= -3060 uA: step size of 12
                        amplitude <  -3060 uA: step size of 24
                      This leads to a set of acceptable values that looks like: 
                        [-6120, -6096, ..., -3084, -3060, -3048, ..., -12, 0 ]

                      Values for the pulse duration can be set in steps of 10 us.
                      The acceptable range is between 10 and 2550 us.
    2) Dead zone 0:   Holds the duration of the pause between main and
                      counter pulse in us. Must have an amplitude of 0.
                      Values can be set in steps of 10 us. The acceptable
                      range is between 10 and 2550 us.
    3) Counter pulse: Holds the amplitude and duration of the
                      counter pulse in uA and us.
                      The counter amplitude strength must be
                        -1/4 * main_pulse_amplitude.
                      The counter amplitude duration must be
                         4 * main_pulse_duration.
    4) Dead zone 0:   Must be identical to the atom 2)
    5) Dead zone 1:   Holds the duration of the pause after the pulse was
                      delivered. Must have an amplitude of 0. Values can be 
                      set in steps of 80 us. The acceptable range goes from
                      10 to 20400 us.
                      Note that the steps are starting from 0 while the minimal 
                      value is 10 us. This leads to a set of acceptable values
                      that looks like: [10, 80, 160, 240, ... , 20400]
   
    Stimulation is usually applied between two points: one source
    electrode and one destination electrode (e.g., a ground electrode).
    Here, this concept is generalized to so-called 'virtual 
    electrodes'. A virtual electrode is a non-empty set of electrodes.
    It allows more degrees of freedom to shape the electric field of a
    stimulation. These two sets have to be disjunct (because an 
    electrode is either a source or a destination electrode, not both)
    and non-empty (because at least two electrodes are needed for
    stimulation).
   
    Each electrode is addressed with a positive integer index (i.e.
    uint32_t) and virtual electrodes are defined as sets of uint32_t.
    Depending on the actual implant used, these indices may vary.
    In addition, depending on the actually used implant, the electrode
    indices and the allowed combinations of electrodes into virtual
    electrodes may differ. Please refer to the documentation of the
    used implant for more details on this.
   
    Typical usage:
    1. create stimulationfunction instance with an
        stimulationcommandfactory.
    2. Add an atom to the stimulation function.
    3. Repeat 2. until all atoms are added.
    4. Set repetitions using setRepetitions().
   
    Please note that one function may only contain atoms of the same
    type (e.g., only rectangular atoms).

    By adding the constant SRC_CHANNEL_GROUND_ELECTRODE to the destination
    electrodes, stimulation to ground is enabled.
'''
from ctypes import POINTER, byref, pointer, c_bool, c_uint32, c_uint64, c_size_t, create_string_buffer
from typing import Tuple, List

from pythonapi.pythonapibase import get_api_base, _CAPIEnum, CAPIStatus, opaque_ptr, _Opaque, c_size_t_ptr, _CAPIUint32Set, get_error_message
from pythonapi.stimulationatom import StimulationAtom

class StimulationFunction():
    '''Class representation of a stimulation function.

        Atoms in the function can be iterated.
    '''

    def __init__(self, handle):
        self._handle = handle
        self._iterator_handle = None
        self.valid = True
        
        api = get_api_base()
        self.__registerMethods(api)

    def __registerMethods(self, api):
        '''Register DLL methods used by this class.'''

        ### Functions for stimulation function

        self._stimulationfunction_append = api.dll_instance.stimulationfunction_append
        self._stimulationfunction_append.restype = CAPIStatus
        self._stimulationfunction_append.argtypes = [opaque_ptr, POINTER(opaque_ptr)]

        self._stimulationfunction_getAtomIterator = api.dll_instance.stimulationfunction_getAtomIterator
        self._stimulationfunction_getAtomIterator.restype = CAPIStatus
        self._stimulationfunction_getAtomIterator.argtypes = [opaque_ptr, POINTER(opaque_ptr)]

        self._stimulationfunction_setRepetitions = api.dll_instance.stimulationfunction_setRepetitions
        self._stimulationfunction_setRepetitions.restype = CAPIStatus
        self._stimulationfunction_setRepetitions.argtypes = [opaque_ptr, c_uint32]
        
        self._stimulationfunction_getRepetitions = api.dll_instance.stimulationfunction_getRepetitions
        self._stimulationfunction_getRepetitions.restype = CAPIStatus
        self._stimulationfunction_getRepetitions.argtypes = [opaque_ptr, POINTER(c_uint32)]

        self._stimulationfunction_getName = api.dll_instance.stimulationfunction_getName
        self._stimulationfunction_getName.restype = CAPIStatus
        
        self._stimulationfunction_setName = api.dll_instance.stimulationfunction_setName
        self._stimulationfunction_setName.restype = CAPIStatus
                
        self._stimulationfunction_getDuration = api.dll_instance.stimulationfunction_getDuration
        self._stimulationfunction_getDuration.restype = CAPIStatus
        self._stimulationfunction_getDuration.argtypes = [opaque_ptr, POINTER(c_uint64)]
                
        self._stimulationfunction_getPeriod = api.dll_instance.stimulationfunction_getPeriod
        self._stimulationfunction_getPeriod.restype = CAPIStatus
        self._stimulationfunction_getPeriod.argtypes = [opaque_ptr, POINTER(c_uint64)]
                
        self._stimulationfunction_setVirtualStimulationElectrodes = \
            api.dll_instance.stimulationfunction_setVirtualStimulationElectrodes
        self._stimulationfunction_setVirtualStimulationElectrodes.restype = CAPIStatus
        self._stimulationfunction_setVirtualStimulationElectrodes.argtypes = \
         [opaque_ptr, POINTER(_CAPIUint32Set), POINTER(_CAPIUint32Set), c_bool]
                
        self._stimulationfunction_getVirtualStimulationElectrodes = \
            api.dll_instance.stimulationfunction_getVirtualStimulationElectrodes
        self._stimulationfunction_getVirtualStimulationElectrodes.restype = CAPIStatus
        self._stimulationfunction_getVirtualStimulationElectrodes.argtypes = \
            [opaque_ptr, POINTER(_CAPIUint32Set), POINTER(_CAPIUint32Set)]
            
        self._stimulationfunction_clone = api.dll_instance.stimulationfunction_clone
        self._stimulationfunction_clone.restype = CAPIStatus
        self._stimulationfunction_clone.argtypes = [opaque_ptr, POINTER(opaque_ptr)]
                    
        self._stimulationfunction_hasEqualSignalForm = api.dll_instance.stimulationfunction_hasEqualSignalForm
        self._stimulationfunction_hasEqualSignalForm.restype = CAPIStatus
        self._stimulationfunction_hasEqualSignalForm.argtypes = [opaque_ptr, opaque_ptr, POINTER(c_bool)]
        
        self._stimulationfunction_hasEqualVirtualStimulationElectrodes = \
            api.dll_instance.stimulationfunction_hasEqualVirtualStimulationElectrodes
        self._stimulationfunction_hasEqualVirtualStimulationElectrodes.restype = CAPIStatus
        self._stimulationfunction_hasEqualVirtualStimulationElectrodes.argtypes = \
            [opaque_ptr, opaque_ptr, POINTER(c_bool)]
            
        self._stimulationfunction_usesGroundElectrode = api.dll_instance.stimulationfunction_usesGroundElectrode
        self._stimulationfunction_usesGroundElectrode.restype = CAPIStatus
        self._stimulationfunction_usesGroundElectrode.argtypes = [opaque_ptr, POINTER(c_bool)]

        self._stimulationfunction_destroy = api.dll_instance.stimulationfunction_destroy
        self._stimulationfunction_destroy.restype = CAPIStatus
        self._stimulationfunction_destroy.argtypes = [POINTER(opaque_ptr)]

        ### Functions for stimulation atom iterator

        self._stimulationatomiterator_next = api.dll_instance.stimulationatomiterator_next
        self._stimulationatomiterator_next.restype = CAPIStatus
        self._stimulationatomiterator_next.argtypes = [opaque_ptr]
        
        self._stimulationatomiterator_isDone = api.dll_instance.stimulationatomiterator_isDone
        self._stimulationatomiterator_isDone.restype = CAPIStatus
        self._stimulationatomiterator_isDone.argtypes = [opaque_ptr, POINTER(c_bool)]

        self._stimulationatomiterator_getCurrentItem = api.dll_instance.stimulationatomiterator_getCurrentItem
        self._stimulationatomiterator_getCurrentItem.restype = CAPIStatus
        self._stimulationatomiterator_getCurrentItem.argtypes = [opaque_ptr, POINTER(opaque_ptr)]
        
        self._stimulationatomiterator_destroy = api.dll_instance.stimulationatomiterator_destroy
        self._stimulationatomiterator_destroy.restype = CAPIStatus
        self._stimulationatomiterator_destroy.argtypes = [POINTER(opaque_ptr)]

    def __del__(self):
        '''Destroy the stimulation function handle if it was not 
            invalidated by appending it to a command.
        '''
        if self._iterator_handle is not None:
            self._destroy_iterator_handle()
        if self.valid:
            self._stimulationfunction_destroy(byref(self._handle))

    def __copy__(self):
        '''Create a shallow copy of the function.'''
        
        copy = type(self)(self._handle)
        copy._iterator_handle = self._iterator_handle
        copy.valid = self.valid
        return copy
    
    def __deepcopy__(self, memo):
        '''Make a deep copy of the stimulation function.

           @param memo Extra parameter of the python __deepcopy__
                function.
        '''

        copied_handle = pointer(_Opaque())

        status = self._stimulationfunction_clone(self._handle, byref(copied_handle))

        if status == CAPIStatus.STATUS_OK:
            copy = type(self)(copied_handle)
            copy.valid = self.valid
            return copy
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")

    def __iter__(self) -> StimulationAtom:
        '''Get Iterator to the first atom in this function. '''
        
        if self._iterator_handle is not None:
            self._destroy_iterator_handle()

        self._iterator_handle = pointer(_Opaque())

        status = self._stimulationfunction_getAtomIterator(self._handle, byref(self._iterator_handle))
        
        if status == CAPIStatus.STATUS_OK:
            return self
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")

    def __next__(self) -> StimulationAtom:
        '''Set iterator to the next atom in the function.'''
        
        if self._iterator_is_done():
            raise StopIteration
        else:
            atom = self._get_current_item()
            status = self._stimulationatomiterator_next(self._iterator_handle)
            
            if status == CAPIStatus.STATUS_OK:
                return atom
            else:
                raise RuntimeError(f"{status.name}: {get_error_message()}")

    def _get_current_item(self):
        '''Returns the current item or None if no iterator exists.'''
        
        atom_handle = pointer(_Opaque())

        status = self._stimulationatomiterator_getCurrentItem(self._iterator_handle, byref(atom_handle))
        
        if status == CAPIStatus.STATUS_OK:
            atom = StimulationAtom(atom_handle)
            atom.valid = False
            return atom
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")

    def _iterator_is_done(self):
        '''True if all elements of the container have been traversed.'''
        
        result = c_bool(False)

        status = self._stimulationatomiterator_isDone(self._iterator_handle, byref(result))
        
        if status == CAPIStatus.STATUS_OK:
            return result.value
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")
    
    def _destroy_iterator_handle(self):
        '''Destroy stimulation atom iterator generated by
            self.__iter__.
        '''

        status = self._stimulationatomiterator_destroy(self._iterator_handle)

        if status != CAPIStatus.STATUS_OK:
            raise RuntimeError(f"{status.name}: {get_error_message()}")

    def append(self, atom: StimulationAtom):
        '''Append a stimulation atom to the end of the stimulation
            function.
            Only valid atoms may be appended. An atom is considered
            invalid if one of the following statements hold:
            - IStimulationAtom::TYPE == AT_NOTYPE
            - The atom has a different type than the other atoms in 
                the function
        
            Invalidates the given stimulation atom.

           @param atom (Type: StimulationAtom) A stimulation atom to be
                appended.
        '''

        status = self._stimulationfunction_append(self._handle, byref(atom._handle))

        if status == CAPIStatus.STATUS_OK:
            atom.valid = False
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")

    @property
    def repetitions(self) -> int:
        '''Get the number of times the sequence of atoms defined in the
            function will be repeated.
        '''
                
        result = c_uint32(0)

        status = self._stimulationfunction_getRepetitions(self._handle, byref(result))
        
        if status == CAPIStatus.STATUS_OK:
            return result.value
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")

    @repetitions.setter
    def repetitions(self, value: int):
        '''Set the number of times the sequence of atoms defined in the 
            function will be repeated.

           @param value (Type: int) The number of repetitions of 
                the function.
        '''

        status = self._stimulationfunction_setRepetitions(self._handle, c_uint32(value))
        
        if status != CAPIStatus.STATUS_OK:
            raise RuntimeError(f"{status.name}: {get_error_message()}")

    @property
    def name(self) -> str:
        '''Get the name of the function.'''

        buffer_size = 128
        buffer = create_string_buffer(buffer_size)
        string_length_ptr = c_size_t_ptr(c_size_t(0))
                
        status = self._stimulationfunction_getName(self._handle, buffer, buffer_size, string_length_ptr)

        if status == CAPIStatus.STATUS_OK:
            return buffer.value.decode("utf-8")
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")

    @name.setter
    def name(self, value: str):
        '''Set the name of the function.

           @param value (Type: str) The name of the function.
        '''
                
        status = self._stimulationfunction_setName(self._handle, value.encode('utf-8'), len(value))

        if status != CAPIStatus.STATUS_OK:
            raise RuntimeError(f"{status.name}: {get_error_message()}")

    @property
    def duration(self) -> int:
        '''Get the total duration in micros defined by the function
            including the time required for all repetitions.
        
            This property is read-only.
        '''
                
        result = c_uint64(0)

        status = self._stimulationfunction_getDuration(self._handle, byref(result))
        
        if status == CAPIStatus.STATUS_OK:
            return result.value
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")

    @property
    def period(self) -> int:
        '''Get the period of the function. The period is the duration
            of one repetition, i.e. the sum of all atom durations.
        
            This property is read-only.
        '''
                
        result = c_uint64(0)

        status = self._stimulationfunction_getPeriod(self._handle, byref(result))
        
        if status == CAPIStatus.STATUS_OK:
            return result.value
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")

    @property
    def virtual_stim_electrodes(self) -> Tuple[List[int], List[int]]:
        '''Get the virtual electrodes for the stimulation function.'''

        vector_size = 127
        ctypes_vector_t = c_uint32 * vector_size
        source = _CAPIUint32Set(c_size_t(vector_size), ctypes_vector_t())
        destination = _CAPIUint32Set(c_size_t(vector_size), ctypes_vector_t())

        status = self._stimulationfunction_getVirtualStimulationElectrodes( \
            self._handle, byref(source), byref(destination))
        
        if status == CAPIStatus.STATUS_OK:
            return source.elements[:source.size], destination.elements[:destination.size]
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")

    def set_virtual_stim_electrodes(self, channels_sets: Tuple[List[int], List[int]], use_ground_electrode: bool):
        '''Set the virtual electrodes for the stimulation function.
        
            First list must always be the source and the second one
            the destination channels!

            @param channels_sets (Type: Tuple[List[int], List[int]]) 
                Tuple containing the src and dest channel lists.
            @param useGndElectrode (Type: bool) 
                True if stimulation to the ground electrode should be used.
        '''  

        source_vector_size = len(channels_sets[0])
        source_vector = (c_uint32 * source_vector_size)(*channels_sets[0])
        source = _CAPIUint32Set(c_size_t(source_vector_size), source_vector)

        destination_vector_size = len(channels_sets[1])
        destination_vector = (c_uint32 * destination_vector_size)(*channels_sets[1])
        destination = _CAPIUint32Set(c_size_t(destination_vector_size), destination_vector)

        status = self._stimulationfunction_setVirtualStimulationElectrodes( \
            self._handle, byref(source), byref(destination), use_ground_electrode)
        
        if status != CAPIStatus.STATUS_OK:
            raise RuntimeError(f"{status.name}: {get_error_message()}")
        
    def has_equal_signal_form(self, other) -> bool:
        '''Check if another function has the same form (i.e., consist
            of the same number of atoms and the atoms are 
            pairwise equal). The number of repetitions may be different.

           @param other (Type: StimulationFunction) The function to be 
                compared to.
        '''
                
        result = c_bool(False)

        status = self._stimulationfunction_hasEqualSignalForm(self._handle, other._handle, byref(result))
        
        if status == CAPIStatus.STATUS_OK:
            return result.value
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")

    def has_equal_virtual_stim_electrodes(self, other) -> bool:
        '''Check if another function has the same virtual electrodes.

           @param other (Type: StimulationFunction) The function to be 
                compared to.
        '''
                
        result = c_bool(False)

        status = self._stimulationfunction_hasEqualVirtualStimulationElectrodes(self._handle, other._handle, byref(result))
        
        if status == CAPIStatus.STATUS_OK:
            return result.value
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")

    def uses_ground_electrode(self) -> bool:
        '''@return true if stimulation to ground is enabled
        '''
                        
        result = c_bool(False)

        status = self._stimulationfunction_usesGroundElectrode(self._handle, byref(result))
        
        if status == CAPIStatus.STATUS_OK:
            return result.value
        else:
            raise RuntimeError(f"{status.name}: {get_error_message()}")
