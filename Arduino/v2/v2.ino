#include "ultrasonics_adc.hpp"

// output buffers to store the adc outputs when their are repetitons and multiple values are required (Dont do more than 16 repetitions or the bits may overflow if their are 16 4096 outputs (unlikely))
volatile uint32_t output_adcbuffer_0[BUF_SIZE];
volatile uint32_t output_adcbuffer_1[BUF_SIZE];

#include <ArduinoJson.h>
#include "stdio.h"
#include "math.h"
#define HWSERIAL_1 Serial5
#define HWSERIAL_2 Serial4

// Set a bool for the transducer communication functions to set to false if they detect an error.
volatile bool baord_error = false;

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

	//Set teensy trigger pin to an output pin 
	pinMode(9, OUTPUT);
	digitalWrite(9, LOW);

	//Set mux select pins to low
	pinMode(35, OUTPUT);
	pinMode(36, OUTPUT);
	pinMode(37, OUTPUT);
	pinMode(38, OUTPUT);
	digitalWrite(35, LOW);
	digitalWrite(36, LOW);
	digitalWrite(37, LOW);
	digitalWrite(38, LOW);


	Serial.begin(115200);
	HWSERIAL_1.begin(1250000, SERIAL_8N1);
	HWSERIAL_2.begin(1250000, SERIAL_8N1);

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
	}
	else {
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

void sendCmd(byte bytearray[3], int board) {

	// Define the reply data structue
	byte FPGA_reply[3];

	// Clear serial buffer on the correct board
	Serial.clear();
	if (board == 1) {
		HWSERIAL_1.clear();
	}
	else if (board == 2) {
		HWSERIAL_2.clear();
	}

	// Trigger high before write
	digitalWrite(27, HIGH);

	// Send all three command bytes at once to the correct board
	if (board == 1) {
		HWSERIAL_1.write(bytearray, 3);
	}
	else if (board == 2) {
		HWSERIAL_2.write(bytearray, 3);
	}

	// Trigger Low after write
	digitalWrite(27, LOW);

	// Delay to allow FPGA to reply
	delayMicroseconds(200); // This is sufficient for a 4 byte reply at 250000 BAUD


							// Read in the reply one byte at a time
	if (board == 1) {
		FPGA_reply[0] = HWSERIAL_1.read();
		FPGA_reply[1] = HWSERIAL_1.read();
		FPGA_reply[2] = HWSERIAL_1.read();
	}
	else if (board == 2) {
		FPGA_reply[0] = HWSERIAL_2.read();
		FPGA_reply[1] = HWSERIAL_2.read();
		FPGA_reply[2] = HWSERIAL_2.read();
	}

	// Print out the error message if the send command and the echo are different
	if (FPGA_reply[0] != bytearray[0] || FPGA_reply[1] != bytearray[1] || FPGA_reply[2] != bytearray[2]) {
		Serial.print("{\"Status\":\"Fail\", \"Error\":\"Recieved different reply from FPGA\", \"sent\":");
		Serial.print(bytearray[0], HEX);
		Serial.print(bytearray[1], HEX);
		Serial.print(bytearray[2], HEX);
		Serial.print(", \"recieved\":");
		Serial.print(FPGA_reply[0], HEX);
		Serial.print(FPGA_reply[1], HEX);
		Serial.print(FPGA_reply[2], HEX);
		Serial.print("}\n");
		baord_error = true;
	}
	// Otherwise Print out the success command
	else {
		//Serial.print("{\"Status\":\"Success\", \"Sent and recieved the correct reply fromt the FPGA\", \"sent \":");
		//Serial.print(bytearray[0]);
		//Serial.print(bytearray[1]);
		//Serial.print(bytearray[2]);
		/*Serial.print(", \"recieved \":");
		Serial.print(FPGA_reply[0]);
		Serial.print(FPGA_reply[1]);
		Serial.print(FPGA_reply[2]);
		Serial.print("}\n");*/
	}
}

void setOffset(byte clock, double offset, int board, bool enable = true) {
	// clock is the clock on the FPGA corresponding to one of the transducers on the baord 0-87 for the original boards
	//	The structure of the command
	//	  23  22  21  20  19  18  17  16  15  14  13  12  11  10  9   8   7   6   5   4   3   2   1   0
	//	| 1 | 0 | 0 | X | X | X | X | X | 0 | X | X | C | Z | Y | Y | Y | 0 | Y | Y | Y | Y | Y | Y | Y |
	//	X = 7 bit clock select
	//	Y = 10 bit half - phase offset
	//	Z = phase of first oscillation
	//	C = Output enable bit
	if (clock > 0b01111111) {
		Serial.print("{\"Status\":\"Fail\", \"Error\":\"Transducer number selected is too large!\"}\n");
		baord_error = true;
	}
	else {
		int offset_int = (2500 - 1250 * (offset / (2 * 3.14159265359)));

		int sign = 0;
		offset_int = offset_int % 1250;
		if (offset_int > 624) {
			sign = 1;
			offset_int = offset_int - 624;
		}

		// Place the first 7 bits of the offset into the low_offset byte
		byte low_offset = offset_int & 0b01111111;

		// Place the remaining 3 bits of the offset, plus the sign bit, into the high offset
		byte high_offset = ((offset_int >> 7) & 0b00000111) + (sign << 3);

		// The command byte has the command bit set, plus 5 bits of the clock select
		byte b1 = 0b10000000 | (clock >> 2);

		// The next bit has the output enable bit set high, plus the last two bits of the clock select, and the high offset bits
		byte enable_bit = 0b00010000;
		if (enable == false) {
			enable_bit = 0b00000000;
		}
		byte b2 = enable_bit | ((clock & 0b00000011) << 5) | high_offset;

		// The last byte contains the low offset bits
		byte b3 = low_offset;

		// Set the command inot a byte array
		byte bytearray[3];
		bytearray[0] = b1;
		bytearray[1] = b2;
		bytearray[2] = b3;

		sendCmd(bytearray, board);
	}
}

int get_board_outputs(int board) {
	byte bytearray[3];

	// Send FPGA command to get the number of outputs
	bytearray[0] = 0b11000000;
	bytearray[1] = 0b00000000;
	bytearray[2] = 0b00000000;

	return getonewordreply(bytearray, board);
}

int getVersion(int board) {
	byte bytearray[3];

	// Send FPGA command to get the version number
	bytearray[0] = 0b11101000;
	bytearray[1] = 0b00000000;
	bytearray[2] = 0b00000000;

	return getonewordreply(bytearray, board);
}

void loadOffsets(int board) {
	byte bytearray[3];

	// Send FPGA command to load the offsets 
	bytearray[0] = 0b11110000;
	bytearray[1] = 0b00000000;
	bytearray[2] = 0b00000000;

	sendCmd(bytearray, board);
}

int getonewordreply(byte bytearray[3], int board) {
	// Define the reply data type
	int FPGA_reply;
	// Send the command to the FPGA and read the reply byte
	sendCmd(bytearray, board);

	if (board == 1) {
		FPGA_reply = HWSERIAL_1.read();
	}
	else if (board == 2) {
		FPGA_reply = HWSERIAL_2.read();
	}
	// Check if a byte is recieved (If not serial.read returns a -1)
	if (FPGA_reply == -1) {
		Serial.print("{\"Status\":\"Fail\", \"Error\":\"Never recieved a reply from the FPGA\"}\n");
		baord_error = true;
	}
	// Retuen the FPGA reply
	return FPGA_reply;
}

void  setOutputDACPower(int power, int board) {
	//	The structure of the command
	//	 23  22  21  20  19  18  17  16  15  14  13  12  11  10  9   8   7   6   5   4   3   2   1   0
	// | 1 | 1 | 1 | X | X | X | X | X | 0 | X | X | X | X | X | X | Y | 0 | Y | Y | Y | Y | Y | Y | Y |
	// X = UNUSED
	// Y = 7 bit DAC value
	if (power > 511) { // DAC goes to 512
		Serial.print("{\"Status\":\"Fail\", \"Error\":\"Power selected is too large!\"}\n");
		baord_error = true;
	}
	else {
		byte bytearray[3];
		bytearray[0] = 0b11100000;
		bytearray[1] = 0b00000011 & (power >> 7);
		bytearray[2] = 0b01111111 & power;

		sendCmd(bytearray, board);
	}
}

void setOutputDACDivisor(int divisor, int board) {
	//	The structure of the command
	//	 23  22  21  20  19  18  17  16  15  14  13  12  11  10  9   8   7   6   5   4   3   2   1   0
	//	| 1 | 0 | 1 | Y | Y | Y | Y | Y | 0 | Y | Y | Y | Y | Y | Y | Y | 0 | Y | Y | Y | Y | Y | Y | Y |
	//	X = UNUSED
	//	Y = 19 bit DAC value
	if (divisor > 0b1111111111111111111) {
		Serial.print("{\"Status\":\"Fail\", \"Error\":\"DAC dicisor selected is too large!\"}\n");
		baord_error = true;
	}
	//else if (divisor < 50) {
	//	Serial.print("{\"Status\":\"Fail\", \"Error\":\"You'll burn out the board if the divisor is too low (<50).\"}\n");
	//	baord_error = true;
	//}
	else {
		byte bytearray[3];
		bytearray[0] = 0b10100000 | (0b00011111 & (divisor >> 14));
		bytearray[1] = 0b01111111 & (divisor >> 7);
		bytearray[2] = 0b01111111 & divisor;

		sendCmd(bytearray, board);
	}
}

void setOutputDACFreq(double freq, int board) {
	//setOutputDACPower(128, board); // 50 % duty cycle, turns the board off and on for equal amounts of time
	int divisor_int = 5e7 / (freq * 1024) - 1;
	setOutputDACDivisor(divisor_int, board);
}

void disableOutput(int clock, int board) { // clock is the clock on the FPGA corresponding to one of the transducers on the baord 0-87 for the original boards
	setOffset(clock, 0, board, false);
}



float Samples_per_wave(void){
	//Measure how long a ADC sample run takes
	elapsedMicros waiting;
	noInterrupts();
	dma0->enable();
	dma2->enable();
	interrupts();
	while (!dma0->complete() || !dma2->complete()) {}
	int duration = waiting;
	float frequency = 1.0 / ((duration / 512.0) * 0.000001);
	float samples_per_wave = frequency / 40000.0;
	//Serial.print("{\"Status\":\"Success\", \"SampleDurations\":");
	//Serial.print(duration);
	//Serial.print(", \"samples_per_wave\":");
	//Serial.print(samples_per_wave);
	//Serial.print("}\n"); //SampleDurations in microseconds
	return samples_per_wave;
}

float time_for_nop_loop(void) {
	//Measure how long a nops take output in nanoseconds
	elapsedMicros waiting;
	for (int i = 0; i < 50000; i = i + 1) { // Mesure how long it takes to do a for loop (three instructions)then 1 nop (one instruction)
		__asm__("nop\n\t");
	};
	float duration = waiting/50.0;
	//Serial.print("{\"Status\":\"Success\", \"nop_Duration\":");
	//Serial.print(duration);
	//Serial.print("}\n");
	return duration;
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
		//First, load the channels to sample from the command, this automatically converts the digital pin number to SC1a numbers which the ADC requires
		for (int i(0); i < 4; ++i) {
			uint16_t SC1A_number_0 = digital_pin_to_sc1a(json_in_root["ADC0Channels"][i].as<uint16_t>(), 0);
			ChannelsCfg_1[i] = 0x40 | SC1A_number_0;
			uint16_t SC1A_number_1 = digital_pin_to_sc1a(json_in_root["ADC1Channels"][i].as<uint16_t>(), 1);
			ChannelsCfg_1[i] = 0x40 | SC1A_number_1;
		}
		// clear output array before looping again
		for (int i = 0; i < BUF_SIZE; ++i) {
			output_adcbuffer_0[i] = 0;
			output_adcbuffer_1[i] = 0;
		}

		digitalWrite(9, HIGH);

		runDMAADC();

		digitalWrite(9, LOW);

		for (int i = 0; i < BUF_SIZE; i = i + 1) {
			output_adcbuffer_0[i] += adcbuffer_0[i];
			output_adcbuffer_1[i] += adcbuffer_1[i];
		}

		delay(3);

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
		// Blank case for now
		break;
	}

	case 4: {
		// Blank case for now
		break;
	}

	case 5: {
		//Start a capture/conversion
		//First, load the channels to sample from the command, this automatically converts the digital pin number to SC1a numbers which the ADC requires
		for (int i(0); i < 4; ++i) {
			uint16_t SC1A_number_1 = digital_pin_to_sc1a(json_in_root["ADC1Channels"][i].as<uint16_t>(), 1);
			ChannelsCfg_1[i] = 0x40 | SC1A_number_1;
		}

		int repetitions_in = json_in_root["repetitions"];
		int* output_array = new int[repetitions_in * BUF_SIZE];
		// clear output array before looping again
		for (int i = 0; i < BUF_SIZE*repetitions_in; ++i) {
			output_array[i] = 0;
		}
		// Checking what the sample rate is and the time delay possible with the nop loop
		float Number_Samples_per_wave = Samples_per_wave();
		float sample_period_nano = (25.0 / Number_Samples_per_wave) * 1000;
		float delay_time_nano = (sample_period_nano / repetitions_in);
		float nop_time_delay = time_for_nop_loop();
		int delay_loops = int(delay_time_nano / nop_time_delay);

		if (repetitions_in == 1) {
			int counter = 0;
			for (int repetitions = 0; repetitions < repetitions_in; repetitions = repetitions + 1) {
				digitalWrite(9, HIGH);
				runDMAADC();
				digitalWrite(9, LOW);

				for (int i = (0); i < BUF_SIZE; i = i + 1) {
					output_array[i + BUF_SIZE * counter] = adcbuffer_1[i];
				}
				counter += 1;
			}
		}
		
		else if (repetitions_in > 1) {
			int counter = 0;
			for (int repetitions = 0; repetitions < repetitions_in; repetitions = repetitions + 1) {
				int loops = delay_loops * repetitions;
				digitalWrite(9, HIGH);
				// nop Delay to change the start time of the mesaurment
				for (int i = 0; i < loops; i = i + 1) {
					__asm__("nop\n\t");
				};
				runDMAADC();
				digitalWrite(9, LOW);

				for (int i = (0); i < BUF_SIZE; i = i + 1) {
					output_array[i + BUF_SIZE * counter] = adcbuffer_1[i];
				}
				counter += 1;

				delay(10); // delay to allow for previous wave to dissapate
			}
		}
		else {
			break;
		}

		delay(1);

		Serial.print("{\"Status\":\"Success\", \"ResultADC1\":[");
		for (int i = 0; i < BUF_SIZE*repetitions_in; i = i + 4) {
			Serial.print(output_array[i]);
			Serial.print(",");
			Serial.print(output_array[i + 1]);
			Serial.print(",");
			Serial.print(output_array[i + 2]);
			Serial.print(",");
			Serial.print(output_array[i + 3]);
			if (i != (BUF_SIZE * repetitions_in) - 4)
				Serial.print(",");
		}
		Serial.print("], \"sample_period_nano\":[");
		Serial.print(sample_period_nano);
		Serial.print("], \"nop_time_delay_nano\":[");
		Serial.print(nop_time_delay);
		Serial.print("], \"nop_loops\":[");
		Serial.print(delay_loops);
		Serial.print("]}\n");
		break;
	}

	case 6: {
		// Mode for testing code
		float Samples_per;
		float time_nop;
		Samples_per = Samples_per_wave();
		time_nop = time_for_nop_loop();
		Serial.println("Samples per wave");
		Serial.println(Samples_per);
		Serial.println("time_for_nop_loop nanoseconds");
		Serial.println(time_nop);
		
		break;
	}
			


	default: {
		Serial.print("{\"Status\":\"Fail\", \"Error\":\"Unrecognised command\"}\n");
		break;
	}
	}
	digitalWrite(ledPin, !digitalRead(ledPin));   //Toggle
}
