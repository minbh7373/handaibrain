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
#include <capi/implantfactory.h>
#include <capi/stimulationcommandfactory.h>
#include <capi/stimulationfunction.h>

#include <stdio.h>
#include <string.h>
#include <stdbool.h>

#define STRING_BUFFER_SIZE 256

static bool g_measurementIsRunning;
static bool g_stimulationIsRunning;

/************************************* Example how to define stimulation commands **************************************/
/*
* Create and append a stimulation atom to a stimulation function.
* @return status information on the success of the operation
*/
capi_status_t append4RectStimulation(HIStimulationFactory hStimCommandFactory, 
    HIStimulationFunction hStimFunction, double value, uint64_t duration)
{
    HIStimulationAtom atomHandle;
    capi_status_t status = 
        stimulationcommandfactory_create4RectStimulationAtom(hStimCommandFactory, &atomHandle, value, 0, 0, 0, duration);
    if (status != STATUS_OK)
    {
        return status;
    }
    // This leads to automatic destruction of the stimulation atom 
    // -> No need to call stimulationatom_destroy
    return stimulationfunction_append(hStimFunction, &atomHandle);
}

/*
* Create and append a stimulation pause atom to a stimulation function.
* @return status information on the success of the operation
*/
capi_status_t appendStimulationPause(HIStimulationFactory hStimCommandFactory,
    HIStimulationFunction hStimFunction, uint64_t duration)
{
    HIStimulationAtom atomHandle;
    capi_status_t status =
        stimulationcommandfactory_createStimulationPauseAtom(hStimCommandFactory, &atomHandle, duration);
    if (status != STATUS_OK)
    {
        return status;
    }
    // This leads to automatic destruction of the stimulation atom 
    // -> No need to call stimulationatom_destroy
    return stimulationfunction_append(hStimFunction, &atomHandle);
}

/*
* Define set of working electrodes (source channels) and counter electrodes (destination channels) for a 
* function represented by the functionHandle.
*
* @param functionHandle Initialized function handle
* @return status information on the success of the operation
*/
capi_status_t addStimulationChannels(HIStimulationFunction functionHandle)
{
    capi_uint32_set_t sourceChannels;
    sourceChannels.size = 1U;
    uint32_t source = 0U;
    sourceChannels.elements = &source;

    capi_uint32_set_t destinationChannels;
    destinationChannels.size = 1U;
    uint32_t destination = 1U;
    destinationChannels.elements = &destination;

    return stimulationfunction_setVirtualStimulationElectrodes(functionHandle, &sourceChannels, &destinationChannels, false);
}

/*
* Define an example stimulation commmand that consists of two stimulation functions:
*
* 1) A Stimulation Pulse (that repeats several times)
* 2) A Stimulation Pause
*
* Note that a stimulation pulse (1) has to conatin exactly five stimulation atoms forming a stimulation cove of the form
*         ____
*   _   _|    |____
*    | |
*    |_|
*
* A pause (2) always consists of one pause atom containing the pause length
*/
capi_status_t createStimulationCommand(HIStimulationFactory factoryHandle, HIStimulationCommand commandHandle)
{
    HIStimulationFunction functionHandle;
    
    // 1) Stimulation Pulse
    capi_status_t status = stimulationcommandfactory_createStimulationFunction(factoryHandle, &functionHandle);
    if (status != STATUS_OK)
    {
        return status;
    }
    
    status = stimulationfunction_setRepetitions(functionHandle, 10);
    if (status != STATUS_OK)
    {
        return status;
    }
    
    status = append4RectStimulation(factoryHandle, functionHandle, 1000.0, 400);
    if (status != STATUS_OK)
    {
        return status;
    }
    status = append4RectStimulation(factoryHandle, functionHandle, 0, 2550);
    if (status != STATUS_OK)
    {
        return status;
    }
    status = append4RectStimulation(factoryHandle, functionHandle, -250.0, 1600);
    if (status != STATUS_OK)
    {
        return status;
    }
    status = append4RectStimulation(factoryHandle, functionHandle, 0, 2550);
    if (status != STATUS_OK)
    {
        return status;
    }
    status = append4RectStimulation(factoryHandle, functionHandle, 0, 2550);
    if (status != STATUS_OK)
    {
        return status;
    }

    status = addStimulationChannels(functionHandle);
    if (status != STATUS_OK)
    {
        return status;
    }

    // Appending of command also leads to destruction of the stimulation function 
    // -> No need to call stimulationfunction_destroy
    // -> If further stimulations are needed, a new function needs to be created
    status = stimulationcommand_append(commandHandle, &functionHandle);
    if (status != STATUS_OK)
    {
        return status;
    }

    // 2) Stimulation Pause
    status = stimulationcommandfactory_createStimulationFunction(factoryHandle, &functionHandle);
    if (status != STATUS_OK)
    {
        return status;
    }

    status = appendStimulationPause(factoryHandle, functionHandle, 30000);
    if (status != STATUS_OK)
    {
        return status;
    }

    return  stimulationcommand_append(commandHandle, &functionHandle);
}


/**********************************  Implemenattion of listener callbacks  ********************************************
* Important: The implant system sends a large amount of events (e.g. onData will be called an average of once per ms).
*            Therefore, the consumer code should avoid expensive operations without decoupling the listener e.g via
*            buffering the data.
*/

void onStimulationStateChanged(const bool isStimulating)
{
    if (isStimulating)
    {
        printf("Stimulation running...\n");
        g_stimulationIsRunning = true;
    }
    else
    {
        printf("Not stimulating...\n");
        g_stimulationIsRunning = false;
    }

}

void onMeasurementStateChanged(const bool isMeasuring)
{
    if (isMeasuring)
    {
        printf("Measurement running...\n");
        g_measurementIsRunning = true;
    }
    else
    {
        printf("Not measuring...\n");
        g_measurementIsRunning = false;
    }
}

void onConnectionStateChanged(
    const connection_type_t connectionType,
    const connection_state_t connectionState)
{

}

void onData(const sample_t* const sample)
{
    // The content of sample is only valid inside this callback. A copy is required for later processing.
    if (sample->numberOfMeasurements > 0)
    {
        printf("Measured: %10.2f \n", sample->measurements[0]);
    }
}

void onImplantVoltageChanged(const double voltageMicroV)
{
    static size_t eventCounter = 0;
    if (eventCounter % 1000 == 0) // during measurement callback can potentially cbe alled once every ms
    {
         printf("*** Voltage received:  %10.2f microvolts.\n", voltageMicroV);
    }
    ++eventCounter;
}

void onPrimaryCoilCurrentChanged(const double currentMilliA)
{

}

void onImplantControlValueChanged(const double controlValue)
{

}

void onTemperatureChanged(const double temperature)
{
    printf("New Temperature: %10.2f (degree Celsius)\n", temperature);
}

void onHumidityChanged(const double humidity)
{
    printf("New Humidity: %10.2f (percent rh)\n", humidity);
}

void onError(const char* errorDescription)
{
    printf(errorDescription);
    printf("\n");
}

void onDataProcessingTooSlow()
{
    printf("Data processing too slow\n");
}

void onStimulationFunctionFinished(const uint64_t numFinishedFunctions)
{
    printf("Stim functions finished: %llu", numFinishedFunctions);
    printf("\n");
}

capi_status_t initializeCallbacks(implantlistener_t* listener)
{
    listener->onStimulationStateChanged = &onStimulationStateChanged;
    listener->onMeasurementStateChanged = &onMeasurementStateChanged;
    listener->onConnectionStateChanged = &onConnectionStateChanged;
    listener->onData = &onData;
    listener->onImplantVoltageChanged = &onImplantVoltageChanged;
    listener->onPrimaryCoilCurrentChanged = &onPrimaryCoilCurrentChanged;
    listener->onImplantControlValueChanged = &onImplantControlValueChanged;
    listener->onTemperatureChanged = &onTemperatureChanged;
    listener->onHumidityChanged = &onHumidityChanged;
    listener->onError = &onError;
    listener->onDataProcessingTooSlow = &onDataProcessingTooSlow;
    listener->onStimulationFunctionFinished = &onStimulationFunctionFinished;

    return STATUS_OK;
}

/*************************************** auxilliary functions **********************************************************/
void printOnlineHelpMessage()
{
    printf("Press\n");
    printf("'q' to quit\n");
    printf("'m' to start measurement\n");
    printf("'c' to stop measurement and stimulation\n");
    printf("'s' for stimulate\n");
    printf("'i' for impedance measurement\n");
}

capi_status_t startMeasurement(HImplant implantHandle)
{
    capi_uint32_set_t channels;
    channels.size = 0;
    return implant_startMeasurement(implantHandle, channels);
}

capi_status_t startStimulation(HImplant implantHandle)
{
    HIStimulationFactory factoryHandle;
    capi_status_t status = stimulationcommandfactory_getFactoryHandle(&factoryHandle);
    if (status != STATUS_OK)
    {
        return status;
    }
    HIStimulationCommand commandHandle;
    status = stimulationcommandfactory_createStimulationCommand(factoryHandle, &commandHandle);
    if (status != STATUS_OK)
    {
        return status;
    }

    status = createStimulationCommand(factoryHandle, commandHandle);
    if (status != STATUS_OK)
    {
        return status;
    }

    // Command handle will be destroyed automatically
    // -> no need to call stimulationcommand_destroy
    return status = implant_startStimulation(implantHandle, commandHandle);
}

/**
* Start the impedance measurement for channel 1
* 
* If the measurement and/or stimulation is running show an error message instead
*/
capi_status_t startImpedanceMeasurement(HImplant implantHandle)
{
    capi_status_t status = STATUS_RUNTIME_ERROR;
    
    if (g_measurementIsRunning)
    {
        printf("Cannot run impedance test while measuring.\n");
    }
    else if (g_stimulationIsRunning)
    {
        printf("Cannot run impedance test while stimulating.\n");
    }
    else
    {
        double result;
        printf("Start Impedance Calculation\n");
        status = implant_getImpedance(implantHandle, 0, &result);
        if (status == STATUS_OK)
        {
            printf("Calculated Impedance: %.2f Ohm\n", result);
        }
    }
    return status;
}

/****************************************************** main **********************************************************/
int main(int argc, char* argv[])
{
    // file for logging
    capi_char_t fileName[] = "./test.log";

    // initialize implantfactory
    capi_status_t status = implantfactory_init(true, fileName, strlen(fileName));
    if (status != STATUS_OK)
    {
        return 1;
    }

    HImplantFactory factoryHandle;
    status = implantfactory_getFactoryHandle(&factoryHandle);
    if (status != STATUS_OK)
    {
        return 1;
    }

    // Discover implant
    HExternalUnitInfo extUnitInfo[127];

    externalunitinfovector_t externalUnitInfoVector;
    externalUnitInfoVector.count = 127;
    externalUnitInfoVector.vector = extUnitInfo;

    status = implantfactory_getExternalUnitInfos(factoryHandle, &externalUnitInfoVector);
    if (status != STATUS_OK || externalUnitInfoVector.count == 0)
    {
        return 1;
    }

    HExternalUnitInfo info = externalUnitInfoVector.vector[0];

    HImplantInfo implantInfoHandle;
    status = implantfactory_getImplantInfo(factoryHandle, info, &implantInfoHandle);
    if (status != STATUS_OK)
    {
        return 1;
    }

    // Create listener handle
    implantlistener_t listenerAdapter;
    status = initializeCallbacks(&listenerAdapter);
    if (status != STATUS_OK)
    {
        return 1;
    }

    HImplantListener listenerHandle;
    status = implant_createListener(&listenerAdapter, &listenerHandle);
    if (status != STATUS_OK)
    {
        return 1;
    }

    // create implant handle (connects implant) and register listener
    HImplant implantHandle;
    status = implantfactory_create(factoryHandle, externalUnitInfoVector.vector[0], implantInfoHandle, &implantHandle);
    if (status != STATUS_OK)
    {
        return 1;
    }

    status = implant_registerListener(implantHandle, listenerHandle);
    if (status != STATUS_OK)
    {
        return 1;
    }

    g_measurementIsRunning = false;
    g_stimulationIsRunning = false;

    // Basic main event loop
    char s1[2];
    printOnlineHelpMessage();
    while (fgets(s1, 2, stdin))
    {
        if (strcmp("q", s1) == 0) // exit program
        {
            implant_setImplantPower(implantHandle, false);
            if (status != STATUS_OK)
            {
                return 1;
            }

            // We need to destroy the implant handle once it is no longer needed
            status = implant_destroy(&implantHandle);
            if (status != STATUS_OK)
            {
                return 1;
            }
            // We need to destroy the implant listener handle once it is no longer needed
            // Since the implant handle it was registered at, we don't need to unregister the listener before destruction
            status = implant_destroyListener(&listenerHandle);
            if (status != STATUS_OK)
            {
                return 1;
            }
            // We need to destroy implant/external unit infos manually
            status = implantinfo_destroy(&implantInfoHandle);
            if (status != STATUS_OK)
            {
                return 1;
            }
            status = externalunitinfos_destroy(&externalUnitInfoVector);
            if (status != STATUS_OK)
            {
                return 1;
            }
            return 0;
        }
        else if (strcmp("m", s1) == 0) // start measurement
        {
            status = startMeasurement(implantHandle);
            if (status != STATUS_OK)
            {
                return 1;
            }
        }
        else if (strcmp("s", s1) == 0) // start stimulation
        {            
            status = startStimulation(implantHandle);
            if (status != STATUS_OK)
            {
                return 1;
            }
        }
        else if (strcmp("c", s1) == 0) // stop stimulation and measurement
        {
            status = implant_stopMeasurement(implantHandle);
            if (status != STATUS_OK)
            {
                return 1;
            }
        }
        else if (strcmp("i", s1) == 0) // stop stimulation and measurement
        {
            status = startImpedanceMeasurement(implantHandle);
            if (status != STATUS_OK)
            {
                return 1;
            }
            
           
        }
        else
        {
            printOnlineHelpMessage();
        }
    }
}