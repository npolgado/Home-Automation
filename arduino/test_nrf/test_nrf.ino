#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

// Define the pipe address that the receiver will listen on
const uint64_t pipe = 0xE8E8F0F0E1LL;

// Define the payload that the receiver is looking for
const char key_payload[] = "hello";

// Initialize the radio object
RF24 radio(7, 8); // CE, CSN pins

void setup() {
  Serial.begin(9600);
  radio.begin();

  // Set the PA Level low to prevent power supply related issues since this is a
  // getting_started sketch, and the likelihood of close proximity of the devices. RF24_PA_MAX is default.
  radio.setPALevel(RF24_PA_LOW);
  radio.openReadingPipe(1, pipe);
  radio.printDetails();
  radio.startListening();
}

void loop() {
  Serial.println("Looking for payload...");
  if (radio.available()) {
    char received_payload[32];
    radio.read(&received_payload, sizeof(received_payload));
    if (strcmp(received_payload, key_payload) == 0) {
      Serial.println("Received key payload: " + String(key_payload));
    }
  }
  delay(1000);
}
