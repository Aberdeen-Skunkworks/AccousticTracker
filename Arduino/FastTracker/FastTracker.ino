#include "DMAChannel.h"
#include "ADC.h"
#include <ArduinoJson.h>

#define ADC_conv_speed ADC_CONVERSION_SPEED::VERY_HIGH_SPEED
#define ADC_samp_speed ADC_SAMPLING_SPEED::VERY_HIGH_SPEED

//The size of the DMA/ADC buffers. Sizes above 512 don't seem to work, which the datasheet agrees with if the DMA channels are in ELINK mode, which they must be.
#define BUF_SIZE 512
//DMAMEM is just a hint to allocate this in the lower memory addresses. As the stack is in the upper addresses, this should result in the DMA using a different memory controller to the CPU, so neither have to wait for each other
DMAMEM static volatile uint16_t __attribute__((aligned(BUF_SIZE + 0))) adcbuffer_0[BUF_SIZE];
DMAMEM static volatile uint16_t __attribute__((aligned(BUF_SIZE + 0))) adcbuffer_1[BUF_SIZE];

//ChannelsCfg order must be {CH1, CH2, CH3, CH0 }, adcbuffer output will be CH0, CH1, CH2, CH3
//Order must be {Second . . . . . . . . First} no matter the number of channels used.
DMAMEM static volatile uint16_t ChannelsCfg_0 [] =  { 0x46, 0x46, 0x46, 0x46 };  //ADC0: CH0 ad6(A6), CH1 ad7(A7), CH2 ad15(A8), CH3 ad4(A9)
DMAMEM static volatile uint16_t ChannelsCfg_1 [] =  { 0x45, 0x46, 0x47, 0x44 };  //ADC1: CH0 ad4(A17), CH1 ad5(A16), CH2ad6(A18), CH3 ad7(A19)

// output buffers to store the adc outputs when their are repetitons and multiple values are required (Dont do more than 16 repetitions or the bits may overflow if their are 16 4096 outputs (unlikely))
volatile uint16_t output_adcbuffer_0[BUF_SIZE];
volatile uint16_t output_adcbuffer_1[BUF_SIZE];


//Create the ADC and DMA controller objects
ADC *adc = new ADC(); // adc object
DMAChannel* dma0 = new DMAChannel(false);
DMAChannel* dma1 = new DMAChannel(false);
DMAChannel* dma2 = new DMAChannel(false);
DMAChannel* dma3 = new DMAChannel(false);

//Shortcut for the LED pin
const int ledPin = 13;

void setup() {
  //Setup the led
  pinMode(ledPin, OUTPUT);
  delay(500);

  Serial.begin(115200);

  // clear DMA buffer (helps us see when a ADC trigger did not work). Not actually needed.
  for (int i = 0; i < BUF_SIZE; ++i) {
    adcbuffer_0[i] = 0;
    adcbuffer_1[i] = 0;
    output_adcbuffer_0[i] = 0;
    output_adcbuffer_1[i] = 0;

  }
  //Setup the ADC
  setup_adc();
  //Setup the DMA channels
  setup_dma();
}

//These are for the small PWM/Square-wave generator we've implemented so that we can generate pulses exactly timed with the ADC
//This counts how many transitions have been outputted so far
volatile int pwm_counter = 0;
//This is the maximum number of transitions to complete in a single pulse
volatile int pwm_pulse_width = 8;
//The digital pin to output the pulse on
volatile int pwm_pin = 20;
//The timer interrupt used to generate the square wave
IntervalTimer pwm_timer;
//The number of times a sample is repeated when a sample command is sent (The division will be performed externally)
volatile int repetitions = 1;



//This is the callback, called by pwm_timer.
void pwm_isr(void) {
  //First check the current pin state
  bool oldState = digitalRead(pwm_pin);
  //Toggle the pin state to cause a transition
  digitalWrite(pwm_pin, !oldState);//Toggle
  //Increase the counter and check if that's the end of the pulse
  pwm_counter += 1;
  if (pwm_counter > pwm_pulse_width) {
    pinMode(pwm_pin, INPUT_DISABLE);
    pwm_timer.end();
  }
}

//This callback is called whenever a DMA channel has completed all BUF_SIZE reads from its ADC. It resets the DMA controller back to the start clears the interrupt.
void dma0_isr(void) {
  dma0->TCD->DADDR = &adcbuffer_0[0];
  dma0->clearInterrupt();
  //Uncomment below if you want the ADC to continuously sample the pin.
  //dma0->enable();
}

//Exactly the same as dma0_isr
void dma2_isr(void) {
  dma2->TCD->DADDR = &adcbuffer_1[0];
  dma2->clearInterrupt();
  //dma2->enable();
}

void loop() {
  //Try to parse the JSON commands coming in via the serial port
  DynamicJsonBuffer jsonBuffer;
  JsonObject& json_in_root = jsonBuffer.parseObject(Serial, 2);
  if (!json_in_root.success())
    //Parsing failed, try again later
    return;
  

  const JsonVariant& cmd = json_in_root["CMD"];
  if (!cmd.is<int>()) {
    Serial.print("{\"Status\":\"Fail\", \"Error\":\"CMD is not a integer?\"}\n");
    return;
  }
  
  switch (cmd.as<int>()) {
    case 0: {
        //CMD0 is a info request
        jsonBuffer.clear(); //Save memory by clearing the jBuffer for reuse, we can't use json_in_root or anything from it after this though!
        JsonObject& json_out_root = jsonBuffer.createObject();
        json_out_root["Status"] = "Success";
        json_out_root["CompileTime"] = __DATE__ " " __TIME__;
        json_out_root.printTo(Serial);
        Serial.print('\n');
        break;
      }
    case 1: {
        //CMD 1 Reads out the results of the last/ongoing conversion

        Serial.print("{\"Status\":\"Success\", \"ResultADC0\":[");
        for (int i = 0; i < BUF_SIZE; i = i + 4) {
          Serial.print(output_adcbuffer_0[i]);
          Serial.print(",");
          Serial.print(output_adcbuffer_0[i + 1]);
          Serial.print(",");
          Serial.print(output_adcbuffer_0[i + 2]);
          Serial.print(",");
          Serial.print(output_adcbuffer_0[i + 3]);
          if (i != BUF_SIZE - 4)
            Serial.print(",");
        }
        Serial.print("], \"ResultADC1\":[");
        for (int i = 0; i < BUF_SIZE; i = i + 4) {
          Serial.print(output_adcbuffer_1[i]);
          Serial.print(",");
          Serial.print(output_adcbuffer_1[i + 1]);
          Serial.print(",");
          Serial.print(output_adcbuffer_1[i + 2]);
          Serial.print(",");
          Serial.print(output_adcbuffer_1[i + 3]);
          if (i != BUF_SIZE - 4)
            Serial.print(",");
        }
        Serial.print("]}\n");
        
        digitalWrite(ledPin, HIGH);   // set the LED on
        delay(50);                  // wait for a second
        digitalWrite(ledPin, LOW);    // set the LED off
        break;
      }
    case 2: {
        //Start a capture/conversion

        //First, load the channels to sample from the command
        for (int i(0); i < 4; ++i) {
          ChannelsCfg_0[i] = 0x40 | json_in_root["ADC0Channels"][i].as<uint16_t>();
          ChannelsCfg_1[i] = 0x40 | json_in_root["ADC1Channels"][i].as<int>();
        }
        // clear output array before looping again
        for (int i = 0; i < BUF_SIZE; ++i) {
          output_adcbuffer_0[i] = 0;
          output_adcbuffer_1[i] = 0;
         }
        repetitions = json_in_root["repetitions"];
        pwm_pin = json_in_root["PWM_pin"];
        pwm_pulse_width = json_in_root["PWMwidth"];
        pwm_counter = 0;
        
        for (int i = 0; i < repetitions; i = i + 1) {
          if (pwm_pin > -1) {
            pinMode(pwm_pin, OUTPUT);
            digitalWrite(pwm_pin, 0);
          }
          //Don't allow interrupts while we enable all the dma systems
          noInterrupts();
          dma0->enable();
          dma2->enable();
          if (pwm_pin > -1){
            pwm_timer.begin(pwm_isr, 12);  // blinkLED to run every 0.15 seconds
          }
          interrupts();
          delay(5); // !! Important !! Delay to allow the DMA to finish before writing to the output buffer otherwise it will write an empty buffer or old data
          for (int i = 0; i < BUF_SIZE; i = i + 1) {
            output_adcbuffer_0[i] += adcbuffer_0[i];
            output_adcbuffer_1[i] += adcbuffer_1[i];
          }
        }
         
        jsonBuffer.clear(); //Save memory by clearing the jBuffer for reuse, we can't use json_in_root or anything from it after this though!
        JsonObject& json_out_root = jsonBuffer.createObject();
        json_out_root["Status"] = "Success";
        json_out_root.printTo(Serial);
        break;
      }
    default: {
        Serial.print("{\"Status\":\"Fail\", \"Error\":\"Unrecognised command\"}\n");
        break;
      }
  }

  digitalWrite(ledPin, !digitalRead(ledPin));   //Toggle
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

