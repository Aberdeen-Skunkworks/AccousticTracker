
def correlation(signal, target_wave, plot = False):
    """ Correlation function that takes in both a signal and a target wave signal and performes a correlation funciton on them. 
    It will output the index of the signal where the waves correlate most. Comment out the plotting lines to see the correlation plotted.
    """
    import numpy as np
    #Correlate the signal and target wave
    correlation = []
    for i in range(len(signal) - len(target_wave)):
       csum = 0
       for j in range(len(target_wave)):
           csum += signal[i + j] * target_wave[j]
       correlation.append(csum)
    
    # Show the correlator function and both waves on the same plot
    if plot():
        import matplotlib.pyplot as plt
        plt.plot(correlation, linewidth=0.5)
        plt.plot(signal, linewidth=0.5)
        plt.plot(target_wave, linewidth=0.5)
        plt.show()

    #Find the highest correlation index
    maxindex = np.argmax(correlation)
    
    return(maxindex)



