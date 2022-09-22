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
import sys
import os
import datetime
import time

sys.path.append(os.path.abspath("../../pythonapi/src"))

from pythonapi import ImplantFactory, init_implant_factory, ImplantListener, ConnectionType, ConnectionState, Sample, StimulationCommandFactory

is_measurement_active = False
is_stimulation_active = False
    
class ExampleListener(ImplantListener):

    def on_stimulation_state_changed(self, is_stimulating):
        global is_stimulation_active
        print("on_stimulation_state_changed", is_stimulating)
        is_stimulation_active = is_stimulating
        if is_stimulating:
            print("Stimulation running...")
        else:
            print("Stimulation not running...")
    
    def on_measurement_state_changed(self, is_measuring):
        global is_measurement_active
        print("on_measurement_state_changed", is_measuring)
        is_measurement_active = is_measuring
        if is_measuring:
            print("Measurement running...")
        else:
            print("Measurement not running...")

    def on_connection_state_changed(self, connection_type: ConnectionType, connection_state: ConnectionState):
        print("on_connection_state_changed", connection_type.name, connection_state.name)
        if connection_state == ConnectionState.CON_STATE_DISCONNECTED:
            sys.exit(0)
    
    def on_data(self, sample: Sample):
        print("on_data", sample.measurements)
    
    def on_implant_voltage_changed(self, voltage_uV: float):
        print("on_implant_voltage_changed", voltage_uV)
    
    def on_primary_coil_current_changed(self, current_mA: float):
        print("on_primary_coil_current_changed", current_mA)
    
    def on_implant_control_value_changed(self, control_value: float):
        print("on_implant_control_value_changed", control_value)
    
    def on_temperature_changed(self, temperature: float):
        print("on_temperature_changed", temperature)
    
    def on_humidity_changed(self, humidity: float):
        print("on_humidity_changed", humidity)
    
    def on_error(self, error_description: str):
        print("on_error", error_description)
        
    def on_data_processing_too_slow(self):
        print("on_data_processing_too_slow")
    
    def on_stimulation_function_finished(self, num_executed_functions: int):
        print("on_stimulation_function_finished", num_executed_functions)

def print_online_help_message():
    print("Press ")
    print("\t'q' to quit")
    print("\t'm' to start measurement")
    print("\t'c' to stop measurement and stimulation")
    print("\t'i' to measure impedance for channel 0")
    print("\t's' to stimulate (source channel 0 and destination channel 1)")

def append4RectStimulation(factory, function, value, duration):
    '''Create and append a stimulation atom to a stimulation function.'''
    atom = factory.create_4rect_stimulation_atom(value, 0, 0, 0, duration)
    function.append(atom)

def create_stimulation_command():
    '''Define an example stimulation commmand that consists of two stimulation functions:
        
        1) A Stimulation Pulse (that repeats several times)
        2) A Stimulation Pause
       
        Note that a stimulation pulse (1) has to conatin exactly five stimulation atoms forming a stimulation cove of the form
                ____
          _   _|    |____
           | |
           |_|
       
        A pause (2) always consists of one pause atom containing the pause length
    '''

    factory = StimulationCommandFactory()
    cmd = factory.create_stimulation_command()

    pulse_func = factory.create_stimulation_function()
    pulse_func.repetitions = 10
    pulse_func.set_virtual_stim_electrodes(([0], [1]), false)
    pulse_func.name = "PulseExample"

    append4RectStimulation(factory, pulse_func, 1000., 400)
    append4RectStimulation(factory, pulse_func, 0., 2550)
    append4RectStimulation(factory, pulse_func, -250., 1600)
    append4RectStimulation(factory, pulse_func, 0., 2550)
    append4RectStimulation(factory, pulse_func, 0., 2550)

    cmd.append(pulse_func)

    pause_func = factory.create_stimulation_function()
    pause_func.name = "PauseExample"

    pause_atom = factory.create_stimulation_pause_atom(30000)
    pause_func.append(pause_atom)

    cmd.append(pause_func)

    return cmd

if __name__ == "__main__":
    log_file_name = f"{datetime.datetime.now():%Y-%m-%d-%H-%M-%S}_bic_data.log"

    init_implant_factory(True, log_file_name)
    factory = ImplantFactory()

    ext_unit_infos = factory.load_external_unit_infos()
    implant_info = None
    ext_unit_info = None

    for info in ext_unit_infos:
        try:
            implant_info = factory.load_implant_info(info)
            ext_unit_info = info
            print(f"{info.device_id}/{implant_info.device_id}")
        except RuntimeError as e:
            print(f"{info.device_id}/???")
            raise e

    print("Trying to connnect to implant")

    implant = factory.create(ext_unit_info, implant_info)
    print("Connection successfull")

    print("Creating listener")
    listener = ExampleListener()
    implant.register_listener(listener)
    print("Listener created and registered")

    print_online_help_message()
    
    while True:
        user_command  = input('Choose an option: ')

        if 'q' in user_command:
            implant.unregister_listener()
            implant.set_implant_power(False)
            sys.exit(0)
            
        elif 'm' in user_command:
            implant.start_measurement([])

        elif 's' in user_command:
            stim_cmd = create_stimulation_command()
            implant.start_stimulation(stim_cmd)

        elif 'c' in user_command:
            implant.stop_measurement()

        elif 'i' in user_command:
            if not is_measurement_active and not is_stimulation_active:
                imp_value = implant.calculate_impedance(0)
                print(f"Measured impedance: {imp_value}")
            else:
                print("Cannot test impedance while measuring/stimulating")
        else:
            os.system('cls' if os.name=='nt' else 'clear')
            print_online_help_message()   

