#include "DMAChannel.h"
#include "ADC.h"
#include <ArduinoJson.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#define HWSERIAL_1 Serial5
#define HWSERIAL_2 Serial4

#define ADC_conv_speed ADC_CONVERSION_SPEED::MED_SPEED    //VERY_HIGH_SPEED
#define ADC_samp_speed ADC_SAMPLING_SPEED::MED_SPEED

// Temperature reading digital pin number
#define ONE_WIRE_BUS 14
// Setup one wire communications
OneWire oneWire(ONE_WIRE_BUS);
// Pass our oneWire reference to Dallas Temperature.
DallasTemperature sensors(&oneWire);

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
volatile uint32_t output_adcbuffer_0[BUF_SIZE];
volatile uint32_t output_adcbuffer_1[BUF_SIZE];


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
  pinMode(27, OUTPUT);
  digitalWrite(27, LOW);

  //sync pin to low
  pinMode(35, OUTPUT);
  digitalWrite(35, LOW);


  Serial.begin(115200);
  HWSERIAL_1.begin(460800, SERIAL_8N1);
  HWSERIAL_2.begin(460800, SERIAL_8N1);



  // Start up the library
  sensors.begin();

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
volatile int pwm_pin = -1;
//The digital pin to output the pulse on that pulls the transducer low used with the amplification circuit
volatile int pwm_pin_low = -1;
//The timer interrupt used to generate the square wave
IntervalTimer pwm_timer;
//The number of times a sample is repeated when a sample command is sent (The division will be performed externally)
volatile int repetitions = 1;


//This is the callback, called by pwm_timer.
void pwm_isr(void) {

  // Check if 1 pin or 2 pins are to be used in pwm mode
  if (pwm_pin_low > -1) {
    //First check the current pin states
    bool oldState = digitalRead(pwm_pin);
    bool oldState_low = digitalRead(pwm_pin_low);

    //Toggle the pin state to cause a transition (Never have both pins set to high!)
    if (oldState == true) {
      digitalWrite(pwm_pin, !oldState);         //Toggle high pin to low first
      digitalWrite(pwm_pin_low, !oldState_low); //Toggle low pin to high next
    }
    if (oldState == false) {
      digitalWrite(pwm_pin_low, !oldState_low); //Toggle high pin to low first
      digitalWrite(pwm_pin, !oldState);         //Toggle low pin to high next
    }
  } else {
    //First check the current pin state
    bool oldState = digitalRead(pwm_pin);
    //Toggle the pin state to cause a transition
    digitalWrite(pwm_pin, !oldState);//Toggle

  }

  //Increase the counter and check if that's the end of the pulse
  pwm_counter += 1;
  if (pwm_counter > pwm_pulse_width) {
    digitalWrite(pwm_pin, false);
    digitalWrite(pwm_pin_low, false);
    pwm_timer.end();
  }
}

//This callback is called whenever a DMA channel has completed all BUF_SIZE reads from its ADC. It resets the DMA controller back to the start clears the interrupt.
void dma0_isr(void) {
  dma0->clearInterrupt();
  dma0->TCD->DADDR = &adcbuffer_0[0];
  //Uncomment below if you want the ADC to continuously sample the pin.
  //dma0->enable();
}

//Exactly the same as dma0_isr
void dma2_isr(void) {
  dma2->clearInterrupt();
  dma2->TCD->DADDR = &adcbuffer_1[0];
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
        break;
      }
    case 2: {
        //Start a capture/conversion
        //First, load the channels to sample from the command
        for (int i(0); i < 4; ++i) {
          ChannelsCfg_0[i] = 0x40 | json_in_root["ADC0Channels"][i].as<uint16_t>();
          ChannelsCfg_1[i] = 0x40 | json_in_root["ADC1Channels"][i].as<uint16_t>();
        }
        // clear output array before looping again
        for (int i = 0; i < BUF_SIZE; ++i) {
          output_adcbuffer_0[i] = 0;
          output_adcbuffer_1[i] = 0;
        }
        repetitions = json_in_root["repetitions"];
        pwm_pin = json_in_root["PWM_pin"];
        pwm_pin_low = json_in_root["PWM_pin_low"];

        pwm_pulse_width = json_in_root["PWMwidth"];
        const unsigned int pwm_delay = json_in_root["PWMdelay"];
        digitalWrite(27, HIGH);
        for (int i = 0; i < repetitions; i = i + 1) {
          if (pwm_pin > -1) {
            pinMode(pwm_pin, OUTPUT);
            digitalWrite(pwm_pin, true);
            pwm_counter = 0;
          }
          if (pwm_pin_low > -1) {
            pinMode(pwm_pin_low, OUTPUT);
            digitalWrite(pwm_pin_low, false);
          }
          if (digitalRead(pwm_pin) == true && digitalRead(pwm_pin_low) == true) {
            digitalWrite(pwm_pin_low, false);
          }

          //Don't allow interrupts while we enable all the dma systems
          //Interrupts need to be off to enable the dma for minimum time between starts. The need to be back on to allow the dma to run as they work with interupts
          if (pwm_pin > -1) {
            pwm_timer.begin(pwm_isr, 12);  // blinkLED to run every 0.15 seconds
            // To be able to delay in the nanoseconds range a for loop that performs a no operation or nop is used. The for loop takes three cpu instructions and the nop takes one.
            // So in total a PWM delay of 1 will delay the start of the ADC by 4 cpu cycles.
            for (int i = 0; i < pwm_delay; i = i + 1) {
              __asm__("nop\n\t");
            };
          }
          noInterrupts();
          dma0->enable();
          dma2->enable();
          interrupts();

          while (!dma0->complete() || !dma2->complete()) {}

          for (int i = 0; i < BUF_SIZE; i = i + 1) {
            output_adcbuffer_0[i] += adcbuffer_0[i];
            output_adcbuffer_1[i] += adcbuffer_1[i];
          }
          delay(3);
        }
        digitalWrite(27, LOW);

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
        break;
      }
    case 3: {
        //Measure how long a ADC sample run takes
        elapsedMicros waiting;
        noInterrupts();
        dma0->enable();
        dma2->enable();
        interrupts();
        while (!dma0->complete() || !dma2->complete()) {}
        int duration = waiting;
        Serial.print("{\"Status\":\"Success\", \"SampleDurationuS\":");
        Serial.print(duration);
        Serial.print("}\n");
        break;
      }

    case 4: {
        //Measure how long a ADC sample run takes
        elapsedMicros waiting;
        for (int i = 0; i < 46080; i = i + 1) { // Mesure how long it takes to do a for loop (three instructions)then 1 nop (one instruction)
          __asm__("nop\n\t");
        };
        int duration = waiting;
        Serial.print("{\"Status\":\"Success\", \"SampleDurationuS\":");
        Serial.print(duration);
        Serial.print("}\n");
        break;
      }

    case 5: {
        //Measure Temperature of the board using a DS18B20 digital temperature sensor

        //Request temperature from sensor
        sensors.requestTemperatures(); // Send the command to get temperature readings

        // Get temperature by index as there is only 1 sensor it is index 0
        float Temperature = sensors.getTempCByIndex(0);
        // Print out the success command
        Serial.print("{\"Status\":\"Success\", \"Temperature\":");
        Serial.print(Temperature);
        Serial.print("}\n");
        break;
      }
    case 6: {
        //Test pins for new board Flash led on 6 fast then slower
        pinMode(0, OUTPUT);
        pinMode(27, OUTPUT);
        digitalWrite(0, LOW);
        digitalWrite(27, LOW);

        for (int i = 0; i < 200; i = i + 1) {
          delay(10);
          digitalWrite(27, HIGH);
          digitalWrite(0, HIGH);
          delay(10);
          digitalWrite(27, LOW);
          digitalWrite(0, LOW);
          int delay_time = i;
          Serial.println(delay_time);
        }


        // Print out the success command
        Serial.print("{\"Status\":\"Success\", \"Light up\":");
        Serial.print("}\n");
        break;
      }

    case 7: { // Case 7 for board 1 using hardware serial 5 on the teensy

		// Clear serial buffers
		Serial.clear();
		HWSERIAL_1.clear();

		// load in the incoming bytes and set up variables
		int incomingByte_FPGA;
		char Bytestream[] = {json_in_root["Bytestream"]};
		unsigned char byte_a;
		unsigned char byte_b;
		unsigned char byte_c;
	
		Serial.print(Bytestream);

		byte_a = Bytestream[0];
		byte_b = Bytestream[1];
		byte_c = Bytestream[2];
		
		// Trigger high before write
        digitalWrite(27, HIGH);
		// Send all three command bytes at once
        HWSERIAL_1.write(byte_a);
        HWSERIAL_1.write(byte_b);
        HWSERIAL_1.write(byte_c);
		// Trigger Low after write
        digitalWrite(27, LOW);

		// Delay to allow FPGA to reply
        delay(1);

        Serial.println(" ");
        while (HWSERIAL_1.available() > 0) {
		  incomingByte_FPGA = HWSERIAL_1.read();
          Serial.print("From FPGA: ");
          Serial.print(incomingByte_FPGA, DEC);
          Serial.print(" ");
          Serial.println(incomingByte_FPGA, BIN);
        }
        break;
      }

    case 8: {
        int incomingByte;

		digitalWrite(27, HIGH);
        Serial.clear();
        HWSERIAL_2.clear();

        HWSERIAL_2.write(192);
        HWSERIAL_2.write(0);
        HWSERIAL_2.write(0);
        delay(100);
        Serial.println(" ");
        while (HWSERIAL_2.available() > 0) {
          incomingByte = HWSERIAL_2.read();
          Serial.print("From FPGA: ");
          Serial.print(incomingByte, DEC);
          Serial.print(" ");
          Serial.println(incomingByte, BIN);

        }
		digitalWrite(27, LOW);
        break;

      }



    case 9: {

        for (int i = 0; i < 100; i = i + 1) {
          digitalWrite(35, HIGH);
          delay(1);
          digitalWrite(35, LOW);
          delay(1000);
        }

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

