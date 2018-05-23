# Accoustic Tracker
A device that triangulates locations of transducers using other transducers.

The basic idea is that a small microcontroller with three transducers which can both send and recieve signals can also self calibrate their own locations by pinging back and forth between each other (4 are needed to resolve completely, but we'll start with 3). Once their relative positions are established, they can then deduce the locations of other transducers which only transmit using [trilateration](https://en.wikipedia.org/wiki/Trilateration).

Transcieving is slightly challenging as the transducers need high voltages (10V+) to drive them effectively, but the recieving ADC on the microcontroller can only take a small voltage range (0-3.3V), so directly connecting them is going to lead to a "bad time". Also, when transducers recieve they put out an AC signal which we must be careful doesn't go outside our ADC range too. 

# Transducer input stage
We'll tie one side of the transducer to ground as we need it when we drive the transducer later. We want the AC part of the signal though, so we decouple the DC offset of the signal using a small 100nF capacitor. We then center this now-decoupled AC signal in the middle of the ADC range using a resistor divider. This signal might drift outside the range 0-3.3V, so we put a current limiting resistor (1k), then two schottky diodes to shunt over/under voltage to the rails. Schottky diodes are needed as we want them to activate before the internal protection diodes (which do the same thing) inside the microcontroller are activated. We do this as the protection diodes can't take as much current AND we don't want the high voltage running around inside the microcontroller. Hopefully the decoupling capacitor around the microcontroller will pick up these small transient voltages (or we can place one near the schottky diodes).

This is a nice note on [protecting an ADC from overvoltage](http://www.analog.com/en/technical-articles/protecting-adc-inputs.html).

[This is the current design of the input stage, the 10pf capacitor represents the ADC internal capacitance.](http://www.falstad.com/circuit/circuitjs.html?cct=$+1+7.8125e-7+0.7389056098930651+50+5+43%0Av+128+208+128+304+0+2+40000+2.5+0+0+0.5%0Ag+128+304+128+320+0%0Ac+128+208+256+208+0+1.0000000000000001e-7+-2.4703540196844305%0Ar+304+64+304+128+0+10000%0Ar+304+64+304+0+0+10000%0AR+304+0+304+-32+0+0+40+5+0+0+0.5%0Ag+304+128+304+144+0%0Aw+256+208+320+208+0%0Ac+320+208+384+208+0+1e-11+4.9703540196844305%0Ag+384+208+384+320+0%0Ax+-14+287+106+290+4+24+Transducer%0Ax+375+192+619+195+4+24+ADC%5Csinput%5Cscapacitance%0Aw+304+64+256+64+0%0Aw+256+64+256+208+0%0Ax+118+77+248+80+4+24+Bias%5Csvoltage%0Ao+0+1+0+4099+5+0.0015625+0+2+0+3%0Ao+7+1+0+12291+4.993620156365011+0.0002560271871056424+1+2+7+3%0A)

# ADC conversion speed
Speed is essential, as we need to resolve the phase of 40khz signals (so we need at least 800khz sampling).

We should use DMA transfers, following the examples in [this post](https://forum.pjrc.com/threads/30171-Reconfigure-ADC-via-a-DMA-transfer-to-allow-multiple-Channel-Acquisition) which is for using the two ADC's to read 4 channels simultaneously. 

In theory we could overclock the ADC's too. [The results don't seem too bad by increasing the bus speed](https://forum.pjrc.com/threads/30171-Reconfigure-ADC-via-a-DMA-transfer-to-allow-multiple-Channel-Acquisition)
