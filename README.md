<h1 align="center">HOME AUTOMATION</h1>

> the code base and organized notes for a home automation system using `arduino`, `raspberry pi`, and hopefully some `more fun`

## How To Install:

`git clone https://github.com/npolgado/Home-Automation.git`

`cd Home-Automation/`

`python3 -m pip install -r requirements.txt`

## Quickstart:

### the local webserver:

the rasberry pi runs a local webserver using python3 and Flask. To run it...

`python3 raspi/main.py`

### the arduino IoT:

Using arduino uno's we can crete IoT wireless nodes which will communicate with the raspi

- upload the uno_bedroom/uno_bedroom.ino file to your arduino uno, connect an IR LED to pin D3, and a DH11 humidity sensor to pin D2. (WIP: CONNECTION FOR WIRELESS COMM)

## TO DO:

- WIRELESS COMMUNICATION -- THE ESP8266 AT COMMANDS DO NOT WORK??
- Home-Assistance Integration
- HUMIDITY LOGGING FOR FLASK FROM [DHT11](https://www.adafruit.com/product/386)
- SENSORS TO BRING UP
  - ULTRASONIC
  - PWM
  - LIGHTS CONTROLS
  - CAMERAS FROM ANALOG -> DIGITAL + LIVE STREAM
  - MICROPHONES + PROCESSING OFFLOAD
- BACKUP USE NRF24LO1+ but still having issues on raspi side for that
- SCHEMATIC FOR EACH COMPONENT
- DOCUMENT + UPDATE INSTALL + CONFIG

## IC Core Component Requirements

### CURRENT GOAL SETUP

- BASED PIALOHA
  - FLASK SERVER
  - DB
  - MAIN NODE OF COMM
- BED NODE:
  - IR TX
  - COMM
  - DHT11
  - LIGHT SWITCH CONTROL
- CAVE NODE:
  - DHT11
  - COMM
  - LIGHT SWITCH CONTROL
- BATH NODE:
  - COMM
  - MICROPHONE
  - LEDS
  - LIGHT SWITCH CONTROL
- THEATER NODE:
  - COMM
  - DHT11
  - MICROPHONE
- SECURE NODES (ENTRANCE/EXITS):
  - COMM
  - ULTRASONIC
  - MICROPHONE
  - CAMERA
- ALL IC's HAVE SHORE POWER access and are modular around the specific room

## References

[Audio/Visual Lip Reading CNN](https://github.com/astorfi/lip-reading-deeplearning)

[Neural Random Forests](https://arxiv.org/pdf/1604.07143.pdf)

[Network Architecture Guidance](https://stats.stackexchange.com/questions/181/how-to-choose-the-number-of-hidden-layers-and-nodes-in-a-feedforward-neural-netw)

[NRF24LO1+ COMM FROM RASPI TO ARDUINO part 1](https://youtu.be/_68f-yp63ds)

[NRF24LO1+ COMM FROM RASPI TO ARDUINO part 2](https://youtu.be/okdY4fIvysA)

[Raspberry Pi HomeAssistant / Docker / Plex Setup](https://youtu.be/72D3MvPk3Xs)
