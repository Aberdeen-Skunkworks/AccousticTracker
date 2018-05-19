#include "ADC.h"
#include <array>

ADC *adc = new ADC(); // adc object
const int pages = 5;
const int page_size = 1024; //Powers of two are faster

int number_points = page_size * pages;
int counter = 1;
int left_speaker = 22;  // 22 for output, Analog read: A19 on ADC 1
int right_speaker = 20; // 20 for output, Analog read: A9 on ADC 0
int read_left = 38;
int read_right = 23;
int output_of_adc[pages * page_size];
int output_of_adc_sync_1[pages * page_size];
int output_of_adc_sync_2[pages * page_size];
int page_counter = 0;

// the setup routine runs once when you press reset:
void setup() {
  // initialize serial communication at 115200 bits per second:
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(115200);
  analogWriteFrequency(right_speaker, 40000);
  analogWriteFrequency(left_speaker, 40000);
  analogWriteResolution(8);
  pinMode(left_speaker, OUTPUT);
  pinMode(right_speaker, OUTPUT);
  pinMode(read_left, INPUT); // left speaker read pin
  pinMode(read_right, INPUT); // right speaker read pin
  adc->setResolution(12, ADC_0); // set bits of resolution
  adc->setResolution(12, ADC_1);
  adc->setReference(ADC_REFERENCE::REF_3V3);
  adc->setSamplingSpeed(ADC_SAMPLING_SPEED::VERY_HIGH_SPEED);
  adc->setConversionSpeed(ADC_CONVERSION_SPEED::VERY_HIGH_SPEED);
  adc->setAveraging(0, ADC_0); // set number of averages  
  adc->setAveraging(0, ADC_1);
  adc->startSynchronizedContinuous(read_right, read_left);
}


void print_buffer(int* buf) {
  if (page_counter < pages){
    for(int i = page_counter * page_size; i < ((page_counter + 1) * page_size); ++i) {
      Serial.println(buf[i]);
    }
    ++page_counter;
  }

  if (page_counter >= pages){
    Serial.println("finished");
    page_counter = 0;
  }
}

void read_analog() {
  pinMode(left_speaker, INPUT_DISABLE);
  delay(0.25);
  analogWrite(left_speaker, 128);
  for(int i = 0; i < number_points; i = i + 1 ){
    output_of_adc[i] = adc->analogRead(A9, ADC_0); //A9 is right speaker
  }
  pinMode(left_speaker, INPUT_DISABLE);
  Serial.println("finished");
  page_counter = 0;
}


void read_synchronous() {
  pinMode(left_speaker, INPUT_DISABLE);
  delay(0.25);
  analogWrite(left_speaker, 128);
  for(int i = 0; i < number_points; i = i + 1 ){
    ADC::Sync_result output_of_both_adc = adc->readSynchronizedContinuous();
    output_of_adc_sync_1[i] = output_of_both_adc.result_adc0;
    output_of_adc_sync_2[i] = output_of_both_adc.result_adc1;
  }
  pinMode(left_speaker, INPUT_DISABLE);
  Serial.println("finished");
  page_counter = 0;
}


char c=0;

void loop() {
  if (Serial.available()) {
    c = Serial.read();      
    if(c=='s') { // start read only the non powered Transducer
      Serial.println("started");
      read_analog();
    } else if(c=='p'){ // Print only the single transducer to serial
      Serial.println("printing");
      print_buffer(output_of_adc);
    } else if(c=='l') { // toggle led on and off
      digitalWriteFast(LED_BUILTIN, !digitalReadFast(LED_BUILTIN));
        
    } else if(c=='d') { // Read Both ADCs at once
      Serial.println("started");
      read_synchronous();
    } else if(c=='o') { // print first ADC
      Serial.println("printing");
      print_buffer(output_of_adc_sync_1);
    } else if(c=='i') { // print Second ADC
      Serial.println("printing");
      print_buffer(output_of_adc_sync_2);
    }
  }
}


    

