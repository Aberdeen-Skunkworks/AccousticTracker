#include "ADC.h"
#include "DMAChannel.h"

// Speeds can be VERY_LOW_SPEED, LOW_SPEED, MED_SPEED, HIGH_SPEED_16BITS, HIGH_SPEED or VERY_HIGH_SPEED
#define ADC_conv_speed ADC_CONVERSION_SPEED::HIGH_SPEED   
#define ADC_samp_speed ADC_SAMPLING_SPEED::VERY_HIGH_SPEED

//The size of the DMA/ADC buffers. Sizes above 512 don't seem to work, which the datasheet agrees with if the DMA channels are in ELINK mode, which they must be.
#define BUF_SIZE 512
//DMAMEM is just a hint to allocate this in the lower memory addresses. As the stack is in the upper addresses, this should result in the DMA using a different memory controller to the CPU, so neither have to wait for each other
DMAMEM static volatile uint16_t __attribute__((aligned(BUF_SIZE + 0))) adcbuffer_0[BUF_SIZE];
DMAMEM static volatile uint16_t __attribute__((aligned(BUF_SIZE + 0))) adcbuffer_1[BUF_SIZE];

//Table which converts pins to ADC SCA1 control indexes for the Teensy 3.6
//Taken from the teensyduino https://github.com/PaulStoffregen/cores/blob/master/teensy3/analog.c#L412, digital pin to sc1a channel
//255 denotes no ADC connection
static const uint8_t mcb_pin2sc1a[] = {
  5, 14, 8, 9, 13, 12, 6, 7, 15, 4, 3, 19+128, 14+128, 15+128, // 0-13 -> A0-A13
  5, 14, 8, 9, 13, 12, 6, 7, 15, 4, // 14-23 are A0-A9
  255, 255, 255, 255, 255, 255, 255, // 24-30 are digital only
  14+128, 15+128, 17, 18, 4+128, 5+128, 6+128, 7+128, 17+128,  // 31-39 are A12-A20
  255, 255, 255, 255, 255, 255, 255, 255, 255,  // 40-48 are digital only
  10+128, 11+128, // 49-50 are A23-A24
  255, 255, 255, 255, 255, 255, 255, // 51-57 are digital only
  255, 255, 255, 255, 255, 255, // 58-63 (sd card pins) are digital only
  3, 19+128, // 64-65 are A10-A11
  23, 23+128,// 66-67 are A21-A22 (DAC pins)
  1, 1+128,  // 68-69 are A25-A26 (unused USB host port on Teensy 3.5)
  26,        // 70 is Temperature Sensor
  18+128     // 71 is Vref
};

//This returns the lower 6 bits of the SC1A ADC register used to select the correct channel for a digital pin on the Teensy 3.6.
//It should be noted that if using ADC1, then an additional MUX option may need to be set, see adc1_setmux to carry this out.
uint8_t adc_pin2sc1a(uint8_t pin, uint8_t ADC_n) {
  if (ADC_n > 1) return 0; //Check a valid ADC was given
  if (pin >= sizeof(mcb_pin2sc1a)) return 0; //Check its a valid pin number
  
  uint8_t channel = mcb_pin2sc1a[pin]; //Grab the allocated pin
  if (channel == 255) return 0; //Its not available to the ADC so return fail
  if ((channel & 0x80) && (ADC_n != 1)) return 0; //Check the pin is indeed on the correct ADC

  if (!(channel & 0x80))
    return channel; //Its ADC0, so return the channel

  //Its ADC1 so return the lower bits
  return channel & 0x3F;
}

uint8_t adc1_setmux(uint8_t pin) {
  if (pin >= sizeof(mcb_pin2sc1a)) return 0; //Check its a valid pin number
  uint8_t channel = mcb_pin2sc1a[pin]; //Grab the allocated pin
  if (channel == 255) return 0; //Its not available to the ADC so return fail
  if (!(channel & 0x80)) return 0; //This is only valid for ADC1

// ADC1_CFG2[MUXSEL] bit selects between ADCx_SEn channels a and b.
  if (channel & 0x40) {
    ADC1_CFG2 &= ~ADC_CFG2_MUXSEL;
  } else {
    ADC1_CFG2 |= ADC_CFG2_MUXSEL;
  }
  return channel;
}

//ChannelsCfg order must be {CH1, CH2, CH3, CH0 }, adcbuffer output will be CH0, CH1, CH2, CH3
//Order must be {Second . . . . . . . . First} no matter the number of channels used.
DMAMEM static volatile uint16_t ChannelsCfg_0[] = { 0x46, 0x46, 0x46, 0x46 };  //ADC0: CH0 ad6(A6), CH1 ad7(A7), CH2 ad15(A8), CH3 ad4(A9)
DMAMEM static volatile uint16_t ChannelsCfg_1[] = { 0x45, 0x46, 0x47, 0x44 };  //ADC1: CH0 ad4(A17), CH1 ad5(A16), CH2ad6(A18), CH3 ad7(A19)

//Create the ADC and DMA controller objects
ADC *adc = new ADC(); // adc object
DMAChannel* dma0 = new DMAChannel(false);
DMAChannel* dma1 = new DMAChannel(false);
DMAChannel* dma2 = new DMAChannel(false);
DMAChannel* dma3 = new DMAChannel(false);

volatile int dma0_repeats = 0;
volatile int dma2_repeats = 0;
//This callback is called whenever a DMA channel has completed all BUF_SIZE reads from its ADC. It resets the DMA controller back to the start clears the interrupt.
void dma0_isr(void) {
  dma0->clearInterrupt();
  dma0->TCD->DADDR = &adcbuffer_0[0];
  //Uncomment below if you want the ADC to continuously sample the pin.
  if (dma0_repeats > 0) {
    dma0->enable();
    --dma0_repeats;
  }
}
//Exactly the same as dma0_isr, but for dma 2
void dma2_isr(void) {
  dma2->clearInterrupt();
  dma2->TCD->DADDR = &adcbuffer_1[0];
  if (dma2_repeats > 0) {
    dma2->enable();
    --dma2_repeats;
  }
}

void setup_dma() {
  //This sets up the DMA controllers to run the ADCs and transfer out the data
  //dma0/dma2 are responsible for copying out the ADC results when ADC0/ADC1 finishes
  //dma1/dma3 then copy a new configuration into the ADC after dma0/dma2 completes its copy. This allows us to change the pin being read, but also starts the next ADC conversion.

  dma0->begin(true);                 // allocate the DMA channel (there are many, this just grabs the first free one)
  dma0->TCD->SADDR = &ADC0_RA;       // where to read from (the ADC result register)
  dma0->TCD->SOFF = 0;               // source increment each transfer (0=Don't move from the ADC result)
  dma0->TCD->ATTR = 0x101;           // [00000][001][00000][001] [Source Address Modulo=off][Source data size=1][Destination address modulo=0][Destination size=1] pg 554  Used for circular buffers, not needed here
  dma0->TCD->NBYTES = 2;             // bytes per transfer
  dma0->TCD->SLAST = 0;              // Last source Address adjustment (what adjustment to add to the source address at completion of the major iteration count), again, don't move
  dma0->TCD->DADDR = &adcbuffer_0[0];// Destination ADDRess (where to write to)
  dma0->TCD->DOFF = 2;               // Destination address signed OFFset, how to update the destination after each write, 2 bytes as its a 16bit int
  dma0->TCD->DLASTSGA = -2 * BUF_SIZE; //Destination LAST adjustment, adjustment to make at the completion of the major iteration count.
  dma0->TCD->BITER = BUF_SIZE;       // Starting major iteration count (should be the value of CITER)
  dma0->TCD->CITER = BUF_SIZE;       // Current major iteration count (decremented each time the minor loop is completed)
  dma0->triggerAtHardwareEvent(DMAMUX_SOURCE_ADC0);
  dma0->disableOnCompletion();       // require restart of the DMA engine in code
  dma0->interruptAtCompletion();     // Call an interrupt when done
  dma0->attachInterrupt(dma0_isr);   // This is the interrupt to call

  dma1->begin(true);              // allocate the DMA channel
  dma1->TCD->SADDR = &ChannelsCfg_0[0];
  dma1->TCD->SOFF = 2;            // source increment each transfer (n bytes)
  dma1->TCD->ATTR = 0x101;
  dma1->TCD->SLAST = -8;          // num ADC0 samples * 2
  dma1->TCD->BITER = 4;           // num of ADC0 samples
  dma1->TCD->CITER = 4;           // num of ADC0 samples
  dma1->TCD->DADDR = &ADC0_SC1A;  // By writing to the ADC0_SC1A register, a new conversion is started.
  dma1->TCD->DLASTSGA = 0;
  dma1->TCD->NBYTES = 2;
  dma1->TCD->DOFF = 0;
  dma1->triggerAtTransfersOf(*dma0);
  dma1->triggerAtCompletionOf(*dma0);

  dma2->begin(true);              // allocate the DMA channel
  dma2->TCD->SADDR = &ADC1_RA;    // where to read from
  dma2->TCD->SOFF = 0;            // source increment each transfer
  dma2->TCD->ATTR = 0x101;
  dma2->TCD->NBYTES = 2;     // bytes per transfer
  dma2->TCD->SLAST = 0;
  dma2->TCD->DADDR = &adcbuffer_1[0];// where to write to
  dma2->TCD->DOFF = 2;
  dma2->TCD->DLASTSGA = -2 * BUF_SIZE;
  dma2->TCD->BITER = BUF_SIZE;
  dma2->TCD->CITER = BUF_SIZE;
  dma2->triggerAtHardwareEvent(DMAMUX_SOURCE_ADC1);
  dma2->disableOnCompletion();    // require restart in code
  dma2->interruptAtCompletion();
  dma2->attachInterrupt(dma2_isr);

  dma3->begin(true);              // allocate the DMA channel
  dma3->TCD->SADDR = &ChannelsCfg_1[0];
  dma3->TCD->SOFF = 2;            // source increment each transfer (n bytes)
  dma3->TCD->ATTR = 0x101;
  dma3->TCD->SLAST = -8;          // num ADC1 samples * 2
  dma3->TCD->BITER = 4;           // num of ADC1 samples
  dma3->TCD->CITER = 4;           // num of ADC1 samples
  dma3->TCD->DADDR = &ADC1_SC1A;
  dma3->TCD->DLASTSGA = 0;
  dma3->TCD->NBYTES = 2;
  dma3->TCD->DOFF = 0;
  dma3->triggerAtTransfersOf(*dma2);
  dma3->triggerAtCompletionOf(*dma2);

  dma1->enable();
  dma3->enable();
}

void setup_adc() {
  //ADC0
  adc->setAveraging(0, ADC_0); // set number of averages
  adc->adc0->setResolution(12); // set bits of resolution
  adc->setConversionSpeed(ADC_conv_speed, ADC_0); // change the conversion speed
  adc->setSamplingSpeed(ADC_samp_speed, ADC_0); // change the sampling speed
  adc->adc0->setReference(ADC_REFERENCE::REF_3V3);

  //ADC1
  adc->setAveraging(0, ADC_1); // set number of averages
  adc->adc1->setResolution(12); // set bits of resolution
  adc->setConversionSpeed(ADC_conv_speed, ADC_1); // change the conversion speed
  adc->setSamplingSpeed(ADC_samp_speed, ADC_1); // change the sampling speed
  adc->adc1->setReference(ADC_REFERENCE::REF_3V3);

  ADC1_CFG2 |= ADC_CFG2_MUXSEL;

  adc->adc0->enableDMA(); //ADC0_SC2 |= ADC_SC2_DMAEN;  // using software trigger, ie writing to ADC0_SC1A
  adc->adc1->enableDMA();

}

void runDMAADC() {
  //Disable interrupts to make sure that the two dma's are started with the minimum delay
  noInterrupts();
  dma0->enable();
  dma2->enable();
  interrupts(); //Re-enable interrupts, as we need em for the DMA!

          //Now wait till the DMA is complete
  while (!dma0->complete() || !dma2->complete()) {}
}
