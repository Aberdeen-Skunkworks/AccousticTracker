
## Unit Tests

def test_correlation(test):

    import numpy as np
    import math
    import functions
    #try increasing the noise!
    noise_stddev = 0.2
    dt = 0.1
    tmax = 100
    steps = int(tmax/dt)
    pulse_duration = 10
    pulse_start = 15
    
    #Make a noisy background signal
    background_signal = [np.random.normal(0, noise_stddev) for step in range(steps)]
    
    #Make a signal to find
    clean_signal = [math.sin(2 * math.pi * dt * i) for i in range(int(pulse_duration/dt))]
    
    #Add them
    pulse_start_index = int(pulse_start/dt)
    
    signal = background_signal
    for i in range(len(clean_signal)):
       signal[i+pulse_start_index] += clean_signal[i]
    
    #Try correlating against the original wave
    #target_wave=clean_signal
    #Or make it difficult by making a square wave that looks like the sine wave (just showing you
    #can find "similar" signals)
    target_wave=[2 * (v>0) - 1 for v in clean_signal]
    
   
    test_result = functions.correlation(signal, target_wave, True)
    
    if test_result != 150:
        print("Error: correlation test function failed")
    
    else:
        test = True
    return test

# Run Tests
if test_correlation(False):
    print("All Tests Passed")
    

