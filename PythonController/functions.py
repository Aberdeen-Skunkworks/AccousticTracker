# Correlation function



def correlation(signal, target_wave):
    import numpy as np
    #Correlate the signal and target wave
    correlation = []
    for i in range(len(signal) - len(target_wave)):
       csum = 0
       for j in range(len(target_wave)):
           csum += signal[i + j] * target_wave[j]
       correlation.append(csum)
    
    #Show the correlator - Uncomment next three lines to plot correlation
    #import matplotlib.pyplot as plt
    #plt.plot(correlation, linewidth=0.5)
    #plt.show()
    
    #Find the highest correlation index
    maxindex = np.argmax(correlation)
    
    return(maxindex)



