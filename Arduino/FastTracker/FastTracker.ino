// Converted to only 1 buffer per ADC, reduced to a small example.
//Based on Example by SaileNav


#include "DMAChannel.h"
#include "ADC.h" 
#include <ArduinoJson.h>

#define ADC_conv_speed ADC_CONVERSION_SPEED::MED_SPEED
#define ADC_samp_speed ADC_SAMPLING_SPEED::MED_SPEED

#define BUF_SIZE 256

ADC *adc = new ADC(); // adc object

DMAChannel* dma0 = new DMAChannel(false);
DMAChannel* dma1 = new DMAChannel(false);
DMAChannel* dma2 = new DMAChannel(false);
DMAChannel* dma3 = new DMAChannel(false);


//ChannelsCfg order must be {CH1, CH2, CH3, CH0 }, adcbuffer output will be CH0, CH1, CH2, CH3
//Order must be {Second . . . . . . . . First} no matter the number of channels used.
const uint16_t ChannelsCfg_0 [] =  { 0x47, 0x4F, 0x44, 0x46 };  //ADC0: CH0 ad6(A6), CH1 ad7(A7), CH2 ad15(A8), CH3 ad4(A9)
const uint16_t ChannelsCfg_1 [] =  { 0x45, 0x46, 0x47, 0x44 };  //ADC1: CH0 ad4(A17), CH1 ad5(A16), CH2ad6(A18), CH3 ad7(A19)

const int ledPin = 13;

DMAMEM static volatile uint16_t __attribute__((aligned(BUF_SIZE+0))) adcbuffer_0[BUF_SIZE];
DMAMEM static volatile uint16_t __attribute__((aligned(BUF_SIZE+0))) adcbuffer_1[BUF_SIZE];

volatile int d2_active;

void setup() {
  // initialize the digital pin as an output.
  pinMode(ledPin, OUTPUT);
  delay(500); 

  d2_active = 0;
  
  pinMode(2, INPUT_PULLUP);
  pinMode(4, OUTPUT);
  pinMode(6, OUTPUT);

  attachInterrupt(2, d2_isr, FALLING);
  
  Serial.begin(115200);
  
  // clear buffer
  for (int i = 0; i < BUF_SIZE; ++i){
      adcbuffer_0[i] = 50000;
      adcbuffer_1[i] = 50000;
    
  }
   
  setup_adc();
  setup_dma(); 
  
}
elapsedMillis debounce;


void loop() {
DynamicJsonBuffer jBuffer;
JsonObject& root = jBuffer.parseObject(Serial, 1);
if (!root.success())
  return;

if (root.containsKey("CMD") && root.is<const char*>("CMD"))
  Serial.println("Hey I have a command");

root.prettyPrintTo(Serial);


  while(0){     //this is leftover from the original example, it no longer serves a purpose
    uint8_t pin = 0;
    if(d2_active) pin=1;

    if(pin>0){
      
      for (int i = 0; i < BUF_SIZE; i = i + 4){
        int a = adcbuffer_0[i];
        Serial.print(a);
        Serial.print(".");
        int b = adcbuffer_0[i+1];
        Serial.print(b);
        Serial.print(".");
        int c = adcbuffer_0[i+2];
        Serial.print(c);
        Serial.print(".");
        int d = adcbuffer_0[i+3];
        Serial.print(d);
        Serial.print("...");                
        int e = adcbuffer_1[i];
        Serial.print(e);        
        Serial.print(".");
        int f = adcbuffer_1[i+1];
        Serial.print(f);        
        Serial.print(".");
        int g = adcbuffer_1[i+2];
        Serial.print(g);        
        Serial.print(".");                        
        int h = adcbuffer_1[i+3];
        Serial.println(h);

      }

      digitalWrite(ledPin, HIGH);   // set the LED on
      delay(50);                  // wait for a second
      digitalWrite(ledPin, LOW);    // set the LED off

      d2_active = 0;     
    }
  }

  digitalWrite(ledPin, HIGH);   // set the LED on
  delay(100);                  // wait for a second
  digitalWrite(ledPin, LOW);    // set the LED off
  delay(100);   
}

void setup_dma() {
  dma0->begin(true);              // allocate the DMA channel 
  dma0->TCD->SADDR = &ADC0_RA;    // where to read from
  dma0->TCD->SOFF = 0;            // source increment each transfer
  dma0->TCD->ATTR = 0x101;
  dma0->TCD->NBYTES = 2;     // bytes per transfer
  dma0->TCD->SLAST = 0;
  dma0->TCD->DADDR = &adcbuffer_0[0];// where to write to
  dma0->TCD->DOFF = 2; 
  dma0->TCD->DLASTSGA = -2*BUF_SIZE;
  dma0->TCD->BITER = BUF_SIZE;
  dma0->TCD->CITER = BUF_SIZE;    
  dma0->triggerAtHardwareEvent(DMAMUX_SOURCE_ADC0);
  dma0->disableOnCompletion();    // require restart in code
  dma0->interruptAtCompletion();
  dma0->attachInterrupt(dma0_isr);
  
  dma1->begin(true);              // allocate the DMA channel 
  dma1->TCD->SADDR = &ChannelsCfg_0[0];
  dma1->TCD->SOFF = 2;            // source increment each transfer (n bytes)
  dma1->TCD->ATTR = 0x101;
  dma1->TCD->SLAST = -8;          // num ADC0 samples * 2
  dma1->TCD->BITER = 4;           // num of ADC0 samples
  dma1->TCD->CITER = 4;           // num of ADC0 samples
  dma1->TCD->DADDR = &ADC0_SC1A;
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
  dma2->TCD->DLASTSGA = -2*BUF_SIZE;
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

  dma0->enable();
  dma1->enable();
  
  dma2->enable();
  dma3->enable();
}

void setup_adc() {
  //ADC0
  //adc->setAveraging(16, ADC_0); // set number of averages
  adc->adc0->setResolution(12); // set bits of resolution
  adc->setConversionSpeed(ADC_conv_speed, ADC_0); // change the conversion speed
  adc->setSamplingSpeed(ADC_samp_speed, ADC_0); // change the sampling speed
  adc->adc0->setReference(ADC_REFERENCE::REF_3V3);
  
  //ADC1
  //adc->setAveraging(16, ADC_1); // set number of averages
  adc->adc1->setResolution(12); // set bits of resolution
  adc->setConversionSpeed(ADC_conv_speed, ADC_1); // change the conversion speed
  adc->setSamplingSpeed(ADC_samp_speed, ADC_1); // change the sampling speed
  adc->adc1->setReference(ADC_REFERENCE::REF_3V3);
  
  ADC1_CFG2 |= ADC_CFG2_MUXSEL;
  
  adc->adc0->enableDMA(); //ADC0_SC2 |= ADC_SC2_DMAEN;  // using software trigger, ie writing to ADC0_SC1A
  adc->adc1->enableDMA();
  
} 

void d2_isr(void) {
  if(debounce > 200){
    d2_active = 1;
    debounce = 0;
    }
    else{return;}
}

void dma0_isr(void) {
    dma0->TCD->DADDR = &adcbuffer_0[0];
    dma0->clearInterrupt();
    dma0->enable();
    digitalWriteFast(4, HIGH);
    digitalWriteFast(4, LOW);
}

void dma2_isr(void) {
    dma2->TCD->DADDR = &adcbuffer_1[0];
    dma2->clearInterrupt();
    dma2->enable();
    digitalWriteFast(6, HIGH);
    digitalWriteFast(6, LOW);
}
