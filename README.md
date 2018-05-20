# Accoustic Tracker
A device that triangulates locations of transducers using other transducers.

The basic idea is that a small microcontroller with three transducers which can both send and recieve signals can also self calibrate their own locations by pinging back and forth between each other. Once their relative positions are established, they can then deduce the locations of other transducers which only transmit.

There are two electrical tasks. (1) Drive the transducers, (2) sample the transducer

# (1) Driving transducers
For good output power it requires high voltages, we'll try with just 5V for now. Later we might make a H bridge using 2N7000 mosfets (remember to tie gates to ground via 10k resistors to drain them when the device is off). The H bridge needs a high Z mode, at least on one side, to allow the recieving mode to work.

# (2) Reading the transducers
The first step is to connect transducers to the Analogue-Digital converter. Transducers produce AC, so we'll tie one side to ground, but then decouple the DC offset of the signal using a small capacitor. Then we create a voltage reference in the middle of the ADC range and add that as an offset. 
[Circuit simulation for level shifting the tranducer signal](http://www.falstad.com/circuit/circuitjs.html?cct=$+1+7.8125e-7+0.7389056098930651+50+5+43%0Av+128+208+128+304+0+2+40000+2.5+0+0+0.5%0Ag+128+304+128+320+0%0Ac+128+208+256+208+0+1.0000000000000001e-7+-2.4703540196844305%0Ar+304+64+304+128+0+10000%0Ar+304+64+304+0+0+10000%0AR+304+0+304+-32+0+0+40+5+0+0+0.5%0Ag+304+128+304+144+0%0Aw+256+208+320+208+0%0Ac+320+208+384+208+0+1e-11+4.9703540196844305%0Ag+384+208+384+320+0%0Ax+-14+287+106+290+4+24+Transducer%0Ax+375+192+619+195+4+24+ADC%5Csinput%5Cscapacitance%0Aw+304+64+256+64+0%0Aw+256+64+256+208+0%0Ax+118+77+248+80+4+24+Bias%5Csvoltage%0Ao+0+1+0+4099+5+0.0015625+0+2+0+3%0Ao+7+1+0+12291+4.993620156365011+0.0002560271871056424+1+2+7+3%0A)

We might have to [protect the ADC from overvoltage](http://www.analog.com/en/technical-articles/protecting-adc-inputs.html) due to the potentially higher voltage of the driving circuit or strong signals. We can just use shottkey diodes if it becomes a problem but the currents involved are tiny, so we might just rely on the internal protection diodes, as this is cheap and cheerful. 

Speed is essential, as we need to resolve the phase of 40khz signals.

We should use DMA transfers, following the examples in [this post](https://forum.pjrc.com/threads/30171-Reconfigure-ADC-via-a-DMA-transfer-to-allow-multiple-Channel-Acquisition) which is for using the two ADC's to read 4 channels simultaneously. 

In theory we could overclock the ADC's too. [The results don't seem too bad by increasing the bus speed](https://forum.pjrc.com/threads/30171-Reconfigure-ADC-via-a-DMA-transfer-to-allow-multiple-Channel-Acquisition)
