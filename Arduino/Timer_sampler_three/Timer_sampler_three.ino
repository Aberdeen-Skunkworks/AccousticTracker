#include "ADC.h"
#include <array>

ADC *adc = new ADC(); // adc object
const int pages = 1;
const int page_size = 512; //Powers of two are faster

int number_points = page_size * pages;
int counter = 1;
int speaker_1_out = 17;   // 17 for output, Analog read: A2 on ADC 0 or ADC 1 
int speaker_2_out = 22;  // 22 for output, Analog read: A19 on ADC 1
int speaker_3_out = 20;  // 20 for output, Analog read: A9 on ADC 0
int read_1 = 16;
int read_2 = 38;
int read_3 = 23;
int output_of_adc[pages * page_size];
int output_of_speaker_1[pages * page_size];
int output_of_speaker_2[pages * page_size];
int output_of_speaker_3[pages * page_size];
int page_counter = 0;

// the setup routine runs once when you press reset:
void setup() {
  // initialize serial communication at 115200 bits per second:
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(500000);
  analogWriteFrequency(speaker_1_out, 40000);
  analogWriteFrequency(speaker_2_out, 40000);
  analogWriteFrequency(speaker_3_out, 40000);
  analogWriteResolution(8);
  pinMode(read_1, INPUT); // speaker 1 read pin
  pinMode(read_2, INPUT); // speaker 2 read pin
  pinMode(read_3, INPUT); // speaker 3 read pin
  adc->setResolution(10, ADC_0); // set bits of resolution
  adc->setResolution(10, ADC_1);
  adc->setReference(ADC_REFERENCE::REF_3V3);
  adc->setSamplingSpeed(ADC_SAMPLING_SPEED::VERY_HIGH_SPEED);
  adc->setConversionSpeed(ADC_CONVERSION_SPEED::VERY_HIGH_SPEED);
  adc->setAveraging(0, ADC_0); // set number of averages  
  adc->setAveraging(0, ADC_1);
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



IntervalTimer pulseTimer;
volatile int pulsePin;

void endPulse() { 
  pinMode(speaker_1_out, INPUT_DISABLE);
  pinMode(speaker_2_out, INPUT_DISABLE);
  pinMode(speaker_3_out, INPUT_DISABLE);
  pulseTimer.end();
}




void read_analog(int pulse_pin = speaker_1_out, int ADC_channel = A2, int sel_ADC = ADC_0) {
  if (pulse_pin != -1) {
    pulsePin = pulse_pin;
    pinMode(pulse_pin, INPUT_DISABLE);
    delay(0.25);
    analogWrite(pulse_pin, 128);
    const int pulse_duration = 4; //Ping for 8 oscillations
    pulseTimer.begin(endPulse, 25 * pulse_duration);
  }
    for(int i = 0; i < number_points; i = i + 1 ){
      output_of_adc[i] = adc->analogRead(ADC_channel, sel_ADC); //A9 is right speaker
   }
  Serial.println("reading done");
  page_counter = 0;
 }





void read_synchronous(int pulse_pin, int read_speaker) {
  analogWrite(pulse_pin, 128);
  const int pulse_duration = 4; //Ping for 4 oscillations
  pulseTimer.begin(endPulse, 25 * pulse_duration);
  for(int i = 0; i < number_points; i = i + 1 ){
    if ((pulse_pin == speaker_1_out and read_speaker == read_2) or (pulse_pin == speaker_2_out and read_speaker == read_1)){
      ADC::Sync_result output_of_both_adc = adc->analogSyncRead(read_1, read_2);
      output_of_speaker_1[i] = output_of_both_adc.result_adc0;
      output_of_speaker_2[i] = output_of_both_adc.result_adc1;
 } else if ((pulse_pin == speaker_1_out and read_speaker == read_3) or (pulse_pin == speaker_3_out and read_speaker == read_1)){
      ADC::Sync_result output_of_both_adc = adc->analogSyncRead(read_3, read_1);
      output_of_speaker_3[i] = output_of_both_adc.result_adc0;
      output_of_speaker_1[i] = output_of_both_adc.result_adc1;
 } else if ((pulse_pin == speaker_2_out and read_speaker == read_3) or (pulse_pin == speaker_3_out and read_speaker == read_2)){
      ADC::Sync_result output_of_both_adc = adc->analogSyncRead(read_3, read_2);
      output_of_speaker_3[i] = output_of_both_adc.result_adc0;
      output_of_speaker_2[i] = output_of_both_adc.result_adc1;
}
}
  pinMode(pulse_pin, INPUT_DISABLE);
  Serial.println("reading done");
  page_counter = 0;
}





char c=0;

void loop() {
  if (Serial.available()) {
    c = Serial.read();
       
      if(c=='p'){ // Print only the single transducer to serial
      Serial.println("printing");
      print_buffer(output_of_adc);
      
    } else if(c=='l') { // toggle led on and off
      digitalWriteFast(LED_BUILTIN, !digitalReadFast(LED_BUILTIN));
      
    } else if(c=='b') { // Background voltage check speaker 1
      Serial.println("started reading");
      read_analog(-1);
    } else if(c=='n') { // Background voltage check speaker 2
      Serial.println("started reading");
      read_analog(-1,A19,ADC_1); 
    } else if(c=='m') { // Background voltage check speaker 3
      Serial.println("started reading");
      read_analog(-1,A9,ADC_0); 

    } else if(c=='d') { // ping 1 listen 2
      Serial.println("started reading");
      read_synchronous(speaker_1_out, read_2);
    } else if(c=='f') { // ping 2 listen 1
      Serial.println("started reading");
      read_synchronous(speaker_2_out, read_1);
    } else if(c=='g') { // ping 1 listen 3
      Serial.println("started reading");
      read_synchronous(speaker_1_out, read_3);
    } else if(c=='h') { // ping 3 listen 1
      Serial.println("started reading");
      read_synchronous(speaker_3_out, read_1);
    } else if(c=='j') { // ping 2 listen 3
      Serial.println("started reading");
      read_synchronous(speaker_2_out, read_3);
    } else if(c=='k') { // ping 3 listen 2
      Serial.println("started reading");
      read_synchronous(speaker_3_out, read_2);

      
    } else if(c=='o') { // print speaker 1
      Serial.println("printing");
      print_buffer(output_of_speaker_1);
    } else if(c=='i') { // print speaker 2
      Serial.println("printing");
      print_buffer(output_of_speaker_2);
    } else if(c=='u') { // print speaker 3
      Serial.println("printing");
      print_buffer(output_of_speaker_3);
    }
  }
} 


    

