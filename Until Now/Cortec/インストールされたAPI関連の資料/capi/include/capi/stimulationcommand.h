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
#ifndef CAPI_STIMULATIONCOMMAND_H
#define CAPI_STIMULATIONCOMMAND_H

#include <capi/capi.h>
#include <capi/stimulationfunction.h>
#include <capi/stimulationfunctioniterator.h>

/**
* @file stimulationcommand.h
* @brief A stimulation command defines a sequence of stimulation functions, which are executed one after the other by the 
*        implant.
*
* This is a generic interface that is intended to be used with different types of implants with different 
* stimulation capabilities each. Stimulation capabilities may vary regarding the number of channels used for 
* stimulation, stimulation amplitude, form of the stimulation signal over time. To reflect this, a stimulation
* command consists of a sequence of stimulation functions. A stimulation function can be composed arbitrarily
* complex.
*
* Each command holds a tracing id that can be set arbitrarily. This id is used to identify executions of the
* command in the application logs.
*
* The execution of a command can be executed internally by setting a number of repetitions > 1. This number of
* repetitions differs from the repetitions of stimulation functions, since all functions in the command are repeated.
*
* Example: Given a command that contains stimulation function A and B and a repetition number of 3. Then, the
* command functions will be executed as follows:
*
* A | B | A | B | A | B
*
* If for the function A, the repetition number is set to 2 additionally, the execution changes to:
*
* A | A | B | A | A | B | A | A | B
*
*
* Typical usage of a stimulation command:
* 1. Create an empty stimulation command instance (with stimulation command factory)
* 2. Repeatedly add stimulationFunction instances
* 3. Send stimulation command to implant by calling implant_startStimulation().
*
* @see implant.h
* @see stimulationfunction.h
*/

/// opaque handle type for passing IStimulationCommand. handle is obtained from stimulationcommandfactory
typedef struct _HIStimulationCommand* HIStimulationCommand; 

#ifdef __cplusplus
extern "C" {
#endif

/**
* Append a stimulation function. The sequence of appends defines the sequence of execution.
*
* Note: The command takes ownership of the function and destroys it automatically at the end of its lifecycle.
*
* @param [in] hStimulationCommand  Handle to stimulation command.
* @param [in] hStimulationFunction Address of handle to stimulation function.
*
* @return Indicator for successful code execution (STATUS_OK on success)
*/
CAPI_DLL capi_status_t stimulationcommand_append(
    HIStimulationCommand  hStimulationCommand,
    HIStimulationFunction* hStimulationFunction);

/**
* Get an iterator that can be used to iterate through all functions currently contained in the stimulation command.
*
* Note: The ownership of the iterator is passed to the caller and must be destroyed with 
*        stimulationfunctioniterator_destroy (@see stimulationfunctioniterator.h) once the iterator is no longer needed.
*
* @param [in] hStimulationCommand           Handle to stimulation command.
* @param [out] hStimulationFunctionIterator Address of handle to stimulationfunctioniterator.
*
* @return Indicator for successful code execution (STATUS_OK on success)
*/
CAPI_DLL capi_status_t stimulationcommand_getFunctionIterator(
    HIStimulationCommand  hStimulationCommand,
    HIStimulationFunctionIterator* hStimulationFunctionIterator);

/**
* Get a function iterator that can be used to iterate through all functions. In contrast
* to the other iterators the iterator is aware of command repetitions. For example, if a command has n
* repetitions, then the iterator will iterate over the functions in the command in sequential order.
*
* Note: The ownership of the iterator is passed to the caller and must be destroyed with
*        stimulationfunctioniterator_destroy (@see stimulationfunctioniterator.h) once the iterator is no longer needed.
*
* @param [in] hStimulationCommand           Handle to stimulation command.
* @param [out] hStimulationFunctionIterator Address of handle to stimulationfunctioniterator.
*
* @return Indicator for successful code execution (STATUS_OK on success)
*/
CAPI_DLL capi_status_t stimulationcommand_getCommandRepetitionAwareFunctionIterator(
    HIStimulationCommand  hStimulationCommand,
    HIStimulationFunctionIterator* hStimulationFunctionIterator);

/**
* Get a function iterator that can be used to iterate through all functions. In contrast
* to getFunctionIterator the iterator is fully aware of function repetitions. For example, if a function has n 
* repetitions, then the iterator will return the next stimulation function after n calls to getNext().
*
* Note: The ownership of the iterator is passed to the caller and must be destroyed with 
*        stimulationfunctioniterator_destroy (@see stimulationfunctioniterator.h) once the iterator is no longer needed.
*
* @param [in] hStimulationCommand           Handle to stimulation command.
* @param [out] hStimulationFunctionIterator Address of handle to stimulationfunctioniterator.
*
* @return Indicator for successful code execution (STATUS_OK on success)
*/
CAPI_DLL capi_status_t stimulationcommand_getRepetitionAwareFunctionIterator(
    HIStimulationCommand  hStimulationCommand,
    HIStimulationFunctionIterator* hStimulationFunctionIterator);

/**
* Get the total duration of the stimulation command in microseconds. Is aware of command repetitions.
*
* @param [in] hStimulationCommand Handle to stimulation command.
* @param [out] duration           Duration of the stimulation command in microseconds.
*
* @return Indicator for successful code execution (STATUS_OK on success)
*/
CAPI_DLL capi_status_t stimulationcommand_getDuration(
    HIStimulationCommand  hStimulationCommand,
    uint64_t* const duration);

/**
* Set the name of the stimulation command.
*
* @param[in] hStimulationCommand Handle to stimulation command.
* @param[in] commandNamePtr      Name to be set.
* @param[in] len                 string length of ptr
*
* @return Indicator for successful code execution (STATUS_OK on success)
*/
CAPI_DLL capi_status_t stimulationcommand_setName(
    HIStimulationCommand  hStimulationCommand,
    const capi_char_t* const commandNamePtr, const size_t len);

/**
* Get the name of the stimulation command. If the command name was not set, empty string is returned.
*
* @param[in] hStimulationCommand Handle to stimulation command.
* @param[out] commandNamePtr     Pointer to buffer, recommended buffer size is 128.
* @param[in] bufferLength        size of the buffer
* @param[out] stringLengthPtr    length of the returned string 
*
* @return Indicator for successful code execution (STATUS_OK on success)
*/
CAPI_DLL capi_status_t stimulationcommand_getName(
    HIStimulationCommand hStimulationCommand,
    capi_char_t* const commandNamePtr,
    const size_t bufferLength, size_t* const stringLengthPtr);

/**
* Make a deep copy of the stimulation command. Caller is responsible for destruction of the copy.
*
* Note: The caller is responsible for destruction of the copy (i.e., via stimulationcommand_destroy)
*
* @param[in] hStimulationCommand       Handle to stimulation command.
* @param[out] hStimulationCommandClone Address of handle to stimulation command.
*
* @return Indicator for successful code execution (STATUS_OK on success)
*/
CAPI_DLL capi_status_t stimulationcommand_clone(
    HIStimulationCommand hStimulationCommand,
    HIStimulationCommand* const hStimulationCommandClone);

/**
* Get the number of stimulation functions in the command. The given size is only aware of 
* command repetitions but not function repetitions.
*
* @param[in] hStimulationCommand Handle to stimulation command.
* @param[out] size               Number of functions in the command.
*
* @return Indicator for successful code execution (STATUS_OK on success)
*/
CAPI_DLL capi_status_t stimulationcommand_getSize(
    HIStimulationCommand hStimulationCommand,
    uint64_t* const size);

/**
* Access the commands tracing id.
*
* @param[in] hStimulationCommand Handle to stimulation command.
* @param[out] id                 Tracing id of the command.
*
* @return Indicator for successful code execution (STATUS_OK on success)
*/
CAPI_DLL capi_status_t stimulationcommand_getTracingId(HIStimulationCommand hStimulationCommand, uint16_t* const id);

/**
* Set the commands tracing id.
*
* @param[in] hStimulationCommand Handle to stimulation command.
* @param[in] id The tracing id.
*
* @return Indicator for successful code execution (STATUS_OK on success)
*/
CAPI_DLL capi_status_t stimulationcommand_setTracingId(HIStimulationCommand hStimulationCommand, const uint16_t id);

/**
* Access the commands repetitions number.
*
* @param[in] hStimulationCommand Handle to stimulation command.
* @param[out] repetitions        Number of repetitions of the command.
*
* @return Indicator for successful code execution (STATUS_OK on success)
*/
CAPI_DLL capi_status_t stimulationcommand_getRepetitions(HIStimulationCommand hStimulationCommand, uint16_t* const repetitions);

/**
* Set the number of times the functions in the command should be repeated.
*
* @param[in] hStimulationCommand Handle to stimulation command.
* @param[in] repetitions The number of repetitions.
*
* @return Indicator for successful code execution (STATUS_OK on success)
*/
CAPI_DLL capi_status_t stimulationcommand_setRepetitions(HIStimulationCommand hStimulationCommand, const uint16_t repetitions);

/**
* Destroy stimulation command handle.
*
* Note: Use this method only if the command has not been used to start stimulation on an implant,
*       since the implant will already take care of its destruction.
*       All stimulation functions added to the command via append will be destroyed as well.
*
* @param[in] hStimulationCommand Address of stimulation command handle to be destroyed.
*                                The handle is nulled after destruction.
*
* @return indicator for successful code execution (STATUS_OK on success)
*/
CAPI_DLL capi_status_t stimulationcommand_destroy(HIStimulationCommand* const hStimulationCommand);

#ifdef __cplusplus
}
#endif

#endif // CAPI_STIMULATIONCOMMAND_H