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
#include <cppapi/bicapi.h>
#include <cppapi/IImplantListener.h>
#include <cppapi/IImplantFactory.h>
#include <cppapi/IStimulationCommand.h>
#include <cppapi/IStimulationFunction.h>
#include <cppapi/ImplantInfo.h>
#include <cppapi/ExternalUnitInfo.h>
#include <cppapi/IImplant.h>
#include <cppapi/Sample.h>
#include <cppapi/IStimulationCommandFactory.h>
#include <mutex>

#include <iostream>
#include <memory>
#include <cppapi/bic3232constants.h>

using namespace cortec::implantapi;


/**
  * @brief Writes implant output to std::cout
  *
  * Important: The implant system sends a large amount of events (e.g. onData will be called an average of once per ms).
  *            Therefore, the consumer code should avoid expensive operations without decoupling the listener e.g via
  *            buffering the data.
  */
class CImplantToStdOutListener : public IImplantListener
{
public:    
    virtual ~CImplantToStdOutListener() {}

    // @implements cortec::implantapi::IImplantListener
    virtual void onStimulationStateChanged(const bool isStimulating)
    {
        std::cout << "*** Stimulation state changed: " << isStimulating << std::endl;

        std::lock_guard<std::mutex> lock(m_mutex);
        m_isStimulating = isStimulating;
    }

    bool isStimulating()
    {
        std::lock_guard<std::mutex> lock(m_mutex);
        return m_isStimulating;
    }

    // @implements cortec::implantapi::IImplantListener
    virtual void onMeasurementStateChanged(const bool isMeasuring)
    {
        std::cout << "*** Measurement state changed: " << isMeasuring << std::endl;

        std::lock_guard<std::mutex> lock(m_mutex);
        m_isMeasuring = isMeasuring;
    }

    bool isMeasuring()
    {
        std::lock_guard<std::mutex> lock(m_mutex);
        return m_isMeasuring;
    }

    // @implements cortec::implantapi::IImplantListener 
    virtual void onConnectionStateChanged(const connection_info_t& info)
    {
        if (info.count(ConnectionType::PC_TO_EXT) > 0)
        {
            const bool isConnected = info.at(ConnectionType::PC_TO_EXT) == ConnectionState::CONNECTED;
            std::cout << "*** Connection state from PC to external unit changed: "
                << (isConnected ? "connected" : "disconnected") << std::endl;
        }
        if (info.count(ConnectionType::EXT_TO_IMPLANT) > 0)
        {
            const bool isConnected = info.at(ConnectionType::EXT_TO_IMPLANT) == ConnectionState::CONNECTED;
            std::cout << "*** Connection state from external unit to implant changed: "
                << (isConnected ? "connected" : "disconnected") << std::endl;
        }
    }

    // @implements cortec::implantapi::IImplantListener        
    virtual void onConnectionStateChanged(const bool isConnected)
    {
        std::cout << "*** Connection state changed: " << isConnected << std::endl;
    }

    // @implements cortec::implantapi::IImplantListener
    virtual void onData(const std::vector<CSample>* samples)
    {
        std::cout << "Samples (#" << samples->size() << ")";
        if (!samples->empty())
        {
            // Output only the first data of the first sample, because std::out is too slow to print
            // all data at measurement data at a sampling rate of 1000.0 Hz
            std::cout << " - Sample(0): " 
                << " V: " << samples->at(0).getSupplyVoltage() 
                << " C: " << samples->at(0).isConnected() 
                << " S (id=" << samples->at(0).getStimulationId() 
                << "): " << samples->at(0).isStimulationActive()
                << " Data (#" << samples->at(0).getNumberOfMeasurements() << ")"; 
            if (samples->at(0).getNumberOfMeasurements() > 0)
            {
                std::unique_ptr<double[]> measurements(samples->at(0).getMeasurements());
                std::cout << ": " << measurements[0];
            }
        }

        std::cout << std::endl;

        delete samples;
    }

    // @implements cortec::implantapi::IImplantListener
    virtual void onImplantVoltageChanged(const double voltageMicroV)
    {
        static size_t eventCounter = 0;
        if (eventCounter % 1000 == 0) // during measurement callback can potentially be called once every ms
        {
            std::cout << "*** Voltage received: " << voltageMicroV << " microvolts." << std::endl;
        }
        ++eventCounter;
    }

    // @implements cortec::implantapi::IImplantListener
    virtual void onPrimaryCoilCurrentChanged(const double currentMilliA)
    {
        std::cout << "*** Primary coil current received: " << currentMilliA << " milliamps." << std::endl;
    }

    // @implements cortec::implantapi::IImplantListener
    virtual void onImplantControlValueChanged(const double controlValue)
    {
        std::cout << "*** Implant control value received: " << controlValue << "%." << std::endl;
    }
    
    // @implements cortec::implantapi::IImplantListener
    virtual void onTemperatureChanged(const double temperature)
    {
        std::cout << "*** Temperature received: " << temperature << " degree Celsius." << std::endl;
    }

    // @implements cortec::implantapi::IImplantListener
    virtual void onHumidityChanged(const double humidity)
    {
        std::cout << "*** Humidity received: " << humidity << " %rh." << std::endl;       
    }

    // @implements cortec::implantapi::IImplantListener
    virtual void onError(const std::exception& err)
    {
        std::cerr << "*** Exception received: " << err.what() << std::endl;
    }

    // @implements cortec::implantapi::IImplantListener
    virtual void onDataProcessingTooSlow()
    {
        std::cout << "*** Warning: Data processing too slow" << std::endl;
    }

    // @implements cortec::implantapi::IImplantListener
    virtual void onStimulationFunctionFinished(const uint64_t numFinishedFunctions)
    {
        std::cout << "*** Stimulation functions finished: " << std::to_string(numFinishedFunctions) << std::endl;
    }

private:
    std::mutex m_mutex;

    bool m_isStimulating;
    bool m_isMeasuring;
};

void printOnlineHelpMessage()
{
    std::cout << "Press " << std::endl;
    std::cout << "\t'q' to quit" << std::endl;
    std::cout << "\t'm' to start measurement" << std::endl;
    std::cout << "\t'c' to stop measurement and stimulation" << std::endl;
    std::cout << "\t's' for stimulate" << std::endl;
}

/**
* @return example stimulation command, which must either be passed to startStimulation() or be deleted in order to 
*         prevent memory leaks
*/
IStimulationCommand* createStimulationCommand()
{
    std::unique_ptr<IStimulationCommandFactory> factory(createStimulationCommandFactory());
    
    IStimulationCommand* cmd = factory->createStimulationCommand();
    IStimulationFunction* function = factory->createStimulationFunction();

    // apply signal to stimulation channel 
    std::set<uint32_t> sourceChannels;
    sourceChannels.insert(16u + 7u); // 16 measurement channel, stimulation channels in [0..7] 
    std::set<uint32_t> destinationChannels;
    destinationChannels.insert(BIC3232Constants::c_groundElectrode);

    function->setRepetitions(10);
    function->append(factory->createRectStimulationAtom(5.0, 20000));
    function->append(factory->createRectStimulationAtom(0, 30000));
    function->append(factory->createRectStimulationAtom(10.0, 20000));
    function->append(factory->createRectStimulationAtom(0, 30000));

    function->setVirtualStimulationElectrodes(sourceChannels, destinationChannels, false);
    cmd->append(function);

    function = factory->createStimulationFunction();
    function->setRepetitions(5);
    function->append(factory->createRectStimulationAtom(7.5, 10000));
    function->append(factory->createRectStimulationAtom(10.0, 10000));
    function->append(factory->createRectStimulationAtom(5.0, 10000));
    function->append(factory->createRectStimulationAtom(2.5, 10000));

    function->setVirtualStimulationElectrodes(sourceChannels, destinationChannels, false);
    cmd->append(function);

    function = factory->createStimulationFunction();
    function->setRepetitions(3);
    function->append(factory->createRectStimulationAtom(2.5, 1000));
    function->append(factory->createRectStimulationAtom(1.0, 5000));
    function->append(factory->createRectStimulationAtom(9.0, 2000));
    function->append(factory->createRectStimulationAtom(0, 17000));

    function->setVirtualStimulationElectrodes(sourceChannels, destinationChannels, false);
    cmd->append(function);       
    
    return cmd;
}

int main(int /*argc*/, char * /*argv*/ [])
{
    try
    {
        // file for logging
        std::string fileName = "./test.log";

        // Get implant factory
        std::unique_ptr<IImplantFactory> implantFactory;
        implantFactory.reset(createImplantFactory(true, fileName));

        // Discover implant
        std::vector<CExternalUnitInfo*> exInfos = implantFactory->getExternalUnitInfos();
        if (exInfos.empty())
        {
            throw std::runtime_error("No external unit found");
        }
        std::unique_ptr<CImplantInfo> implantInfo(implantFactory->getImplantInfo(*exInfos.at(0)));

        // Create implant for a specific external unit / implant type
        std::unique_ptr<IImplant> implant(implantFactory->create(*exInfos.at(0), *implantInfo));

        // Register output listener and start measurement loop
        CImplantToStdOutListener listener;
        implant->registerListener(&listener);
        
        // Basic main event loop
        const int16_t stringBufferSize = 256;
        char s1[stringBufferSize];
        printOnlineHelpMessage();
        while (std::cin.getline(s1, stringBufferSize))
        {
            if (strcmp("q", s1) == 0) // exit program
            {
                break;
            }
            else if (strcmp("m", s1) == 0) // start measurement
            {
                implant->startMeasurement();
            }
            else if (strcmp("s", s1) == 0) // start stimulation
            {
                // IStimulationCommand* cmd = createStimulationCommand();
                // implant->startStimulation(cmd);
                std::cout << "Stimulation feature is comming soon." << std::endl;
            }
            else if (strcmp("c", s1) == 0) // stop stimulation and measurement
            {
                implant->stopMeasurement();
            }
            else
            {
                printOnlineHelpMessage();
            }
        }
        implant->setImplantPower(false);
    }
    catch(const std::runtime_error& e)
    {
        std::cerr << e.what() << std::endl;
        return 1;
    }
    catch(const std::exception& e)
    {
        std::cerr << e.what() << std::endl;
        return 2;
    }
    catch(...)
    {
        std::cerr << "Unknown exception." << std::endl;
        return 3;
    }

    return 0;
}