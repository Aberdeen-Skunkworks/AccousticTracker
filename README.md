# Accoustic Tracker
A device that triangulates locations of transducers using other transducers.

The basic idea is that a small microcontroller with three transducers which can both send and recieve signals can also self calibrate their own locations by pinging back and forth between each other (4 are needed to resolve completely, but we'll start with 3). Once their relative positions are established, they can then deduce the locations of other transducers which only transmit using [trilateration](https://en.wikipedia.org/wiki/Trilateration).

Transcieving is slightly challenging as the transducers need high voltages (10V+) to drive them effectively, but the recieving ADC on the microcontroller can only take a small voltage range (0-3.3V), so directly connecting them is going to lead to a "bad time". Also, when transducers recieve they put out an AC signal which we must be careful doesn't go outside our ADC range too. 

# Transducer input stage
We'll tie one side of the transducer to ground as we need it when we drive the transducer later. We want the AC part of the signal though, so we decouple the DC offset of the signal using a small 100nF capacitor. We then center this now-decoupled AC signal in the middle of the ADC range using a resistor divider. This signal might drift outside the range 0-3.3V, so we put a current limiting resistor (1k), then two schottky diodes to shunt over/under voltage to the rails. Schottky diodes are needed as we want them to activate before the internal protection diodes (which do the same thing) inside the microcontroller are activated. We do this as the protection diodes can't take as much current AND we don't want the high voltage running around inside the microcontroller. Hopefully the decoupling capacitor around the microcontroller will pick up these small transient voltages (or we can place one near the schottky diodes).

This is a nice note on [protecting an ADC from overvoltage](http://www.analog.com/en/technical-articles/protecting-adc-inputs.html).

[This is the current design of the input stage, the 10pf capacitor represents the ADC internal capacitance.](http://www.falstad.com/circuit/circuitjs.html?cct=$+1+7.8125e-7+0.48711659992454737+50+5+43%0Av+128+208+128+256+0+2+40000+1+0+0+0.5%0Ag+32+304+32+336+0%0Ac+128+208+256+208+0+1.0000000000000001e-7+8.176974525371321%0Ar+304+64+304+128+0+10000%0Ar+304+64+304+0+0+10000%0AR+304+0+304+-32+0+0+40+3.3+0+0+0.5%0Ag+304+128+304+144+0%0Aw+256+208+320+208+0%0Ac+464+208+528+208+0+1e-11+-0.43156791400295147%0Ag+464+272+464+304+0%0Ax+-27+369+106+399+4+24+Transducer%5C%5CnCapacitance%0Ax+540+221+668+278+4+24+ADC%5C%5Cninput%5C%5Cncapacitance%0Aw+304+64+256+64+0%0Aw+256+64+256+208+0%0Ax+337+42+414+99+4+24+Bias%5C%5Cnvoltage%5C%5Cnsource%0Ac+32+240+32+304+0+1.9e-9+0.013235185355151557%0Aw+32+208+128+208+0%0Ar+-176+128+-240+128+0+2200%0Ar+-48+224+-112+224+0+1000%0Ar+320+208+416+208+0+10000%0Aw+-16+208+-16+144+0%0Aw+-16+144+32+144+0%0Aw+-16+128+-16+144+0%0Ag+-16+240+-16+272+0%0AR+-16+48+-16+16+0+0+40+20+0+0+0.5%0As+128+256+128+304+0+1+false%0Ag+128+304+128+336+0%0Ax+157+278+250+308+4+24+Simulate%5C%5Cninput%0Aw+32+208+32+240+0%0Aw+-112+224+-144+224+0%0Av+-304+128+-240+128+0+2+40000+1.65+1.65+3.141592653589793+0.5%0Av+-304+224+-240+224+0+2+40000+1.65+1.65+0+0.5%0Aw+-304+128+-304+224+0%0Aw+-304+224+-304+272+0%0Ag+-304+320+-304+352+0%0At+-48+224+-16+224+0+1+0.62053318388151+0.6337683692366616+100%0At+-48+112+-16+112+0+-1+19.986764811244925+-3.3999221216163278e-9+100%0At+-176+128+-144+128+0+1+-19.999999996116074+2.639999999684195e-10+100%0Ag+-144+144+-144+160+0%0Ar+-144+112+-96+112+0+1000%0Aw+-16+48+-16+96+0%0Ar+-64+48+-64+112+0+10000%0Aw+-64+48+-16+48+0%0Aw+-48+112+-64+112+0%0Aw+-64+112+-96+112+0%0Aw+-144+224+-240+224+0%0Ad+464+208+464+160+1+0.805904783%0Ad+464+272+464+208+1+0.805904783%0AR+464+160+464+128+0+0+40+3.3+0+0+0.5%0Aw+528+208+528+272+0%0Aw+464+272+528+272+0%0Aw+416+208+464+208+0%0As+-304+272+-304+320+0+0+false%0Ax+-272+295+-183+325+4+24+simulate%5C%5Cndriving%0Aw+32+144+32+208+0%0Ao+8+1+0+4099+5+0.0001953125+0+2+8+3%0Ao+46+1+0+4099+5+0.00625+1+2+46+3%0A)

# ADC conversion speed
Speed is essential, as we need to resolve the phase of 40khz signals (so we need at least 800khz sampling).

We should use DMA transfers, following the examples in [this post](https://forum.pjrc.com/threads/30171-Reconfigure-ADC-via-a-DMA-transfer-to-allow-multiple-Channel-Acquisition) which is for using the two ADC's to read 4 channels simultaneously. 

In theory we could overclock the ADC's too. [The results don't seem too bad by increasing the bus speed](https://forum.pjrc.com/threads/30171-Reconfigure-ADC-via-a-DMA-transfer-to-allow-multiple-Channel-Acquisition)
