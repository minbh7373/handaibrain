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
#ifndef IMPLANTAPI_ISTIMULATION_COMMAND_H
#define IMPLANTAPI_ISTIMULATION_COMMAND_H
#include <cppapi/IIterator.h>
#include <cppapi/IStimulationFunction.h>
#include <stdint.h>


namespace cortec { namespace implantapi {

    /**
      * @brief Interface for classes that can be sent to an implant to elicit electrical stimulation.
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
      * Typical usage of an IStimulationCommand:
      * 1. Create an empty stimulation command instance.
      * 2. Set an id for tracing in the logs.
      * 3. Repeatedly add IStimulationFunction instances.
      * 4. Send IStimulationCommand instance to implant by calling IImplant::startStimulation().
      *
      * @see IImplant
      * @see IStimulationFunction
      */
    class IStimulationCommand
    {
    public:
        virtual ~IStimulationCommand() {}

        /**
          * Append a stimulation function. The sequence of appends defines the sequence of execution.
          * The ownership of IStimulationFunction is passed to the IStimulationCommand if this method call succeeds 
          * (i.e., does not throw and exception).
          *
          * \if INTERN_IMPLANTAPI
          *     @throws CInvalidArgumentException if duration is 0 microseconds or function is a nullptr
          * \else
          *     @throws std::exception if duration is 0 or function is a nullptr
          * \endif
          */
        virtual void append(IStimulationFunction* function) = 0;

        /**
          * Return iterator that can be used to iterate through all functions currently contained in the 
          * IStimulationCommand. It is aware neither of function nor of command repetitions.
          *
          * The ownership of the iterator is passed to the caller.
          *
          * @return iterator pointing to the first IStimulationFunction.
          */
        virtual IIterator<IStimulationFunction>* getFunctionIterator() const = 0;

        /**
        * Return iterator that can be used to iterate through all functions currently contained in the
        * IStimulationCommand and is aware of command repetitions.
        *
        * The ownership of the iterator is passed to the caller.
        *
        * @return iterator pointing to the first IStimulationFunction.
        */
        virtual IIterator<IStimulationFunction>* getCommandRepetitionAwareFunctionIterator() const = 0;

        /**
          * Return function iterator that can be used to iterate through all functions. In contrast
          * to getFunctionIterator the iterator is fully aware of function repetitions (not command repetitions). For example, if a function has n 
          * repetitions, then the iterator will return the next stimulation function after n calls to getNext().
          *
          * The ownership of the iterator is passed to the caller.
          * 
          * @return repetition aware iterator pointing to the first IStimulationFunction
          */
        virtual IIterator<IStimulationFunction>* getRepetitionAwareFunctionIterator() const = 0;

        /**
          * @return the total duration of the stimulation command in microseconds. Is aware of command repetitions.
          */
        virtual uint64_t getDuration() const = 0;

        /**
          * Set the name of the command.
          */
        virtual void setName(const std::string& commandName) = 0;

        /**
          * @return the set name of the command. If the command name was not set, empty string is returned.
          */
        virtual std::string getName() const = 0;

        /**
          * Return a deep copy of the command. Caller is responsible for deletion of the cloned command.
          *
          * @return An identical deep copy of the command.
          */
        virtual IStimulationCommand* clone() const = 0;

        /**
          * @return The number of stimulation functions and pauses. The given size is only aware of 
          * command-repetitions but not function repetitions.
          */
        virtual uint64_t getSize() const = 0;

        /**
        * @return The commands tracing id.
        */
        virtual uint16_t getTracingId() const = 0;

        /**
        * Set the commands tracing id.
        *
        * @param[in] id The tracing id.
        */
        virtual void setTracingId(const uint16_t id) = 0;

        /**
        * @return The number of repetitions of the command execution.
        */
        virtual uint16_t getRepetitions() const = 0;

        /**
        * Set the number of times the functions in the command should be repeated.
        *
        * @param[in] repetitions The number of repetitions.
        *
        * @throws invalid argument exception if number of repetitions is 0.
        */
        virtual void setRepetitions(const uint16_t repetitions) = 0;
    };
}}


#endif //IMPLANTAPI_ISTIMULATION_COMMAND_H