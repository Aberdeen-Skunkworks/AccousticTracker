## Functions used in the main acoustic tracker program


def correlation(signal, target_wave, plot = False):
    """ Correlation function that takes in both a signal and a target wave signal and performes a correlation funciton on them. 
    It will output the index of the signal where the waves correlate most. Comment out the plotting lines to see the correlation plotted.
    """
    import numpy as np
   
    #Correlate the signal and target wave
    correlation_signal = []
    for i in range(len(signal) - len(target_wave)):
       csum = 0
       for j in range(len(target_wave)):
           csum += signal[i + j] * target_wave[j]
       correlation_signal.append(csum)
    
    # Show the correlator function and both waves on the same plot if the user sets plot to True.
    if plot:
        import matplotlib.pyplot as plt
        plt.plot(correlation_signal, linewidth=0.5)
        plt.plot(signal, linewidth=0.5)
        plt.plot(target_wave, linewidth=0.5)
        plt.show()

    #Find the highest correlation index
    maxindex = np.argmax(correlation_signal)
    
    return maxindex, correlation_signal


def target_wave():
    """ Funciton that returns the saved target wave for the correlation funciton to use. This is a 99 sample set of the recieved acoustic signal.
    """

    target = [-62.43359375, -40.43359375, -7.43359375, 34.56640625, 60.56640625, 80.56640625, 71.56640625, 44.56640625, 4.56640625, -38.43359375,
-70.43359375, -85.43359375, -78.43359375, -52.43359375, -9.43359375, 37.56640625, 77.56640625, 98.56640625, 92.56640625, 63.56640625,
13.56640625, -39.43359375, -80.43359375, -101.4335938, -94.43359375, -64.43359375, -15.43359375, 39.56640625, 80.56640625, 103.5664063,
95.56640625, 65.56640625, 16.56640625, -37.43359375, -81.43359375, -105.4335938, -98.43359375, -70.43359375, -22.43359375, 32.56640625,
79.56640625, 103.5664063, 101.5664063, 72.56640625, 22.56640625, -33.43359375, -77.43359375, -103.4335938, -100.4335938, -71.43359375,
-24.43359375, 29.56640625, 75.56640625, 99.56640625, 97.56640625, 70.56640625, 19.56640625, -29.43359375, -72.43359375, -96.43359375,
-93.43359375, -65.43359375, -20.43359375, 30.56640625,70.56640625, 89.56640625, 86.56640625, 58.56640625, 16.56640625, -28.43359375,
-66.43359375, -88.43359375, -84.43359375, -57.43359375, -16.43359375, 29.56640625, 65.56640625, 81.56640625, 77.56640625, 51.56640625,
12.56640625, -27.43359375, -63.43359375, -79.43359375, -74.43359375, -50.43359375, -14.43359375, 26.56640625, 57.56640625, 72.56640625,
66.56640625, 41.56640625, 2.56640625, -33.43359375, -59.43359375, -72.43359375, -65.43359375, -39.43359375, -4.43359375]
    return target