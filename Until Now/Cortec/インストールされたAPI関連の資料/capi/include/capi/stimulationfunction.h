/**********************************************************************
* Copyright 2015-2019, CorTec GmbH
* All rights reserved.
*
* Redistribution, modification, adaptation or translation is not permitted.
*
* CorTec shall be liable a) for any damage caused by a willful, fraudulent or grossly 
* negligent act, or resulting in injury to life, body or health, or covered by the 
* Product Liability Act, b) for any reasonably foreseeable damage resulting from 
* its breach of a fundamental contractual obligation up to the amount of the 
* licensing fees agreed under this Agreement. 
* All other claims shall be excluded. 
* CorTec excludes any liability for any damage caused by Licensee's 
* use of the Software for regular medical treatment of patients.
**********************************************************************/
#ifndef CAPI_STIMULATIONFUNCTION_H
#define CAPI_STIMULATIONFUNCTION_H

#include <capi/capi.h>
#include <capi/stimulationatom.h>

/**
* @file stimulationfunction.h
* @brief stimulation function defines what stimulation signal is applied to which electrodes.
*
* A stimulation function consists of
* - a sequence of stimulation atoms that can be repeated a number of times.
* - and the information which electrodes to use for stimulation.
*
* There are two types of stimulation that consist of the following atoms:
*
* 1) A stimulation pause: one pause atom
* 2) A stimulation pulse: five 4-rect stimulation atoms
*
* The stimulation atoms in the second case each describe one specific part
* of the stimulation pulse, including main and counter pulses as well
* as dead zones between them. The five stimulation atoms form a stimulation cove of the form:
*                   ____
*  Pulse      _   _|    |_ _____
*              | |
*              |_|
*
*  Atom         1 2   3  4   5
*
* Pulse Atom Definition:
*
* 1) Main pulse:    Holds the amplitude and duration of the main pulse in uA and us.
*                   The acceptable value range goes from -6120 to 0 uA. The granularity changes for smaller amplitudes as follows:
*                     amplitude >= -3060 uA: step size of 12
*                     amplitude <  -3060 uA: step size of 24
*                   This leads to a set of acceptable values that looks like: [-6120, -6096, ..., -3084, -3060, -3048, ..., -12, 0 ]
*                   Values for the pulse duration can be set in steps of 10 us. The acceptable range is between 10 and 2550 us.
* 2) Dead zone 0:   Holds the duration of the pause between main and counter pulse in us. Must have an amplitude of 0.
*                   Values can be set in steps of 10 us. The acceptable range is between 10 and 2550 us.
* 3) Counter pulse: Holds the amplitude and duration of the counter pulse in uA and us.
*                   The counter amplitude strength must be -1/4 * main_pulse_amplitude.
*                   The counter amplitude duration must be 4 * main_pulse_duration.
* 4) Dead zone 0:   Must be identical to the atom 2)
* 5) Dead zone 1:   Holds the duration of the pause after the pulse was delivered. Must have an amplitude of 0.
*                   Values can be set in steps of 80 us. The acceptable range goes from 10 to 20400 us.
*                   Note that the steps are starting from 0 while the minimal value is 10 us. This leads to 
*                   a set of acceptable values that looks like: [10, 80, 160, 240, ... , 20400]
*
* Stimulation is usually applied between two points: one source electrode and one destination electrode (e.g., a 
* ground electrode). Here, this concept is generalized to so-called 'virtual electrodes'. A virtual electrode is a
* non-empty set of electrodes. It allows more degrees of freedom to shape the electric field of a stimulation.
* These two sets have to be disjunct (because an electrode is either a source or a destination electrode, not 
* both) and non-empty (because at least two electrodes are needed for stimulation).
*
* Each electrode is addressed with a positive integer index (i.e., uint32_t) and virtual electrodes are defined 
* as sets of uint32_t. Depending on the actual implant used, these indices may vary.
* In addition, depending on the actually used implant, the electrode indices and the allowed combinations of
* electrodes into virtual electrodes may differ. Please refer to the documentation of the used implant for more 
* details on this.
*
* Typical usage:
* 1. create stimulationfunction instance with an stimulationcommandfactory.
* 2. Add an atom to the stimulation function.
* 3. Repeat 2. until all atoms are added.
* 4. Set repetitions using setRepetitions().
*
* Please note that one function may only contain atoms of the same type (e.g., only rectangular atoms).
*
* @see stimulationcommandfactory
* @see stimulationatom
*/

typedef struct _HIStimulationFunction* HIStimulationFunction; ///< opaque type for passing IStimulationFunction

#ifdef __cplusplus
extern "C" {
#endif

/**
* Append a stimulation atom to the end of the stimulation function.
* Only valid atoms may be appended. An atom is considered invalid if one of the following statements hold:
* - IStimulationAtom::TYPE == AT_NOTYPE
* - The atom has a different type than the other atoms in the function
*
* Note: The function takes ownership of the atom and destroys it automatically at the end of its lifecycle.
* 
* @param[in] hStimulationFunction Handle to stimulation function
* @param[inout] hStimulationAtom  Address of handle to stimulation atom.
*               Stimulation function takes ownership of the atom and nulls the handle.
*
* @return Indicator for successful code execution (capi_status_t::STATUS_OK on success)
*/
CAPI_DLL capi_status_t stimulationfunction_append(
    HIStimulationFunction hStimulationFunction, 
    HIStimulationAtom* hStimulationAtom);

/**
* Get Iterator to the first atom in this function. 
*
* Note: The ownership of the iterator is passed to the caller and must be destroyed with stimulationatomiterator_destroy
*       (@see stimulationatomiterator.h) once the iterator is no longer required.
*
* @param[in] hStimulationFunction      Handle to stimulation function.
* @param[out] hStimulationAtomIterator Address of handle to simulation atom.
*
* @return indicator for successful code execution (STATUS_OK on success)
*/
CAPI_DLL capi_status_t stimulationfunction_getAtomIterator(
    HIStimulationFunction hStimulationFunction,
    HIStimulationAtomIterator* hStimulationAtomIterator);

/**
* Set the number of times the sequence of atoms defined in the function will be repeated.
*
* @param[in] hStimulationFunction Handle to stimulation function.
* @param[in] repetitions          Number of times the sequence of atoms defined in the function will be repeated.
*
* @return Indicator for successful code execution (STATUS_OK on success)
*/
CAPI_DLL capi_status_t stimulationfunction_setRepetitions(
    HIStimulationFunction hStimulationFunction, 
    const uint32_t repetitions);

/**
* Get the number of times the sequence of atoms defined in the function will be repeated.
*
* @param[in] hStimulationFunction Handle to stimulation function.
* @param[out] repetitions         Number of times the sequence of atoms defined in the function will be repeated.
*
* @return Indicator for successful code execution (STATUS_OK on success)
*/
CAPI_DLL capi_status_t stimulationfunction_getRepetitions(
    HIStimulationFunction hStimulationFunction, 
    uint32_t* const repetitions);

/**
* Set the name of the function.
*
* @param[in] hStimulationFunction Handle to stimulation function.
* @param[in] functionNamePtr      pointer to function name
* @param[in] len                  string length of function name
* @return Indicator for successful code execution (STATUS_OK on success)
*/
CAPI_DLL capi_status_t stimulationfunction_setName(
    HIStimulationFunction hStimulationFunction,
    const capi_char_t* const functionNamePtr, const size_t len);

/**
* Get the name of the function.
*
* @param[in] hStimulationFunction Handle to stimulation function.
* @param[out] functionNamePtr     buffer for name of the function.
* @param[in] bufferLength         length of buffer for name of the function.
* @param[out] stringLengthPtr     actual string length of the name.
* @return Indicator for successful code execution (STATUS_OK on success)
*/
CAPI_DLL capi_status_t stimulationfunction_getName(
    HIStimulationFunction hStimulationFunction,
    capi_char_t* const functionNamePtr, const size_t bufferLength, size_t* const stringLengthPtr);

/**
* Get the total duration in micros defined by the function including the time required for all repetitions.
*
* @param[in] hStimulationFunction Handle to stimulation function.
* @param[out] duration            Duration of the function in micros.
*
* @return Indicator for successful code execution (STATUS_OK on success)
*/
CAPI_DLL capi_status_t stimulationfunction_getDuration(
    HIStimulationFunction hStimulationFunction,
    uint64_t* const duration);

/**
* Get the period of the function.
* The period is the duration of one repetition, i.e. the sum of all atom durations.
*
* @param[in] hStimulationFunction Handle to stimulation function.
* @param[out] period              Duration of one period of function in micros.
*
* @return Indicator for successful code execution (STATUS_OK on success)
*/
CAPI_DLL capi_status_t stimulationfunction_getPeriod(HIStimulationFunction hStimulationFunction,
    uint64_t* const period);

/**
* Set the virtual electrodes for the stimulation function.
*
* Note: The sets must be disjunct and destinationChannelSet may not be empty.
*
* @param[in] hStimulationFunction  Handle to stimulation function.
* @param[in] sourceChannelSet      Set of electrodes where the function is applied to.
* @param[in] destinationChannelSet Set of electrodes that are used as ground electrodes by this function.
* @param[in] useGndElectrode     True if stimulation to the ground electrode should be used.
*
* @return Indicator for successful code execution (STATUS_OK on success)
*/
CAPI_DLL capi_status_t stimulationfunction_setVirtualStimulationElectrodes(
    HIStimulationFunction hStimulationFunction,
    const capi_uint32_set_t* const sourceChannelSet,
    const capi_uint32_set_t* const destinationChannelSet,
    const bool useGndElectrode);

/**
* Get the virtual electrodes for the stimulation function.
*
* @param[in] hStimulationFunction   Handle to stimulation function.
* @param[out] sourceChannelSet      Set of electrodes where the function is applied to.
* @param[out] destinationChannelSet Set of electrodes that are used as ground electrodes by this function.
*
* @return Indicator for successful code execution (STATUS_OK on success)
*/
CAPI_DLL capi_status_t stimulationfunction_getVirtualStimulationElectrodes(
    HIStimulationFunction hStimulationFunction,
    capi_uint32_set_t* const sourceChannelSet,
    capi_uint32_set_t* const destinationChannelSet);

/**
* Make a deep copy of the stimulation function. 
*
* Note: The caller is responsible for destruction of the copy. E.g. via stimulationfunction_destroy or by passing the
* function to a stimulation command, which takes care of the destruction of its functions.
*
* @param[in] hStimulationFunction       Handle to stimulation function.
* @param[out] hStimulationFunctionClone Address of handle to stimulation function.
*
* @return Indicator for successful code execution (STATUS_OK on success)
*/
CAPI_DLL capi_status_t stimulationfunction_clone(
    HIStimulationFunction hStimulationFunction,
    HIStimulationFunction* const hStimulationFunctionClone);

/**
* Check if another function has the same form (i.e., consist of the same number of atoms and the atoms are 
* pairwise equal). The number of repetitions may be different.
*
* @param[in] hStimulationFunction      Handle to stimulation function.
* @param[in] hOtherStimulationFunction Handle to another stimulation function.
* @param[out] result                   True if the signal form is the same.
*
* @return Indicator for successful code execution (STATUS_OK on success)
*/
CAPI_DLL capi_status_t stimulationfunction_hasEqualSignalForm(
    HIStimulationFunction hStimulationFunction,
    HIStimulationFunction hOtherStimulationFunction, 
    bool* const result);

/**
* Check if another function has the same virtual electrodes.
*
* @param[in] hStimulationFunction      Handle to stimulation function.
* @param[in] hOtherStimulationFunction Handle to another stimulation function.
* @param[out] result                   True if the source electrodes and the destination electrodes are
*             the same for both functions.
*
* @return Indicator for successful code execution (STATUS_OK on success)
*/
CAPI_DLL capi_status_t stimulationfunction_hasEqualVirtualStimulationElectrodes(
    HIStimulationFunction hStimulationFunction,
    HIStimulationFunction hOtherStimulationFunction, 
    bool* const result);

/**
* @param[in] hStimulationFunction Address of handle to stimulation function to be destroyed.
*            The handle is nulled after destruction.
*
* @param[in] result True if stimulation to ground is enabled.
*
* @return Indicator for successful code execution (STATUS_OK on success)
*/
CAPI_DLL capi_status_t stimulationfunction_usesGroundElectrode(
    HIStimulationFunction const hStimulationFunction, bool* const result);

/**
* Destroy stimulation function handle.
*
* Note: Use this method only if the function has not been added to a stimulation command,
*       since the command will already take care of its destruction.
*       All stimulation atoms added to the function via append will be destroyed as well.
*
* @param[in] hStimulationFunction Address of handle to stimulation function to be destroyed.
*            The handle is nulled after destruction.
*
* @return Indicator for successful code execution (STATUS_OK on success)
*/
CAPI_DLL capi_status_t stimulationfunction_destroy(HIStimulationFunction* const hStimulationFunction);

#ifdef __cplusplus
}
#endif

#endif // CAPI_STIMULATIONFUNCTION_H