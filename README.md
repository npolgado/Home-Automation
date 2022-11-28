<h1 align="center">HOME AUTOMATION</h1>

> the code base and organized notes for a home automation system using arduino, and raspberry pi and IoT nodes.

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

- WIRELESS COMMUNICATION -- just get a wifi uno lol
- Setup temperature adjustment based on outside weather
- Setup fan controls
- Add setup.py for easy install
- Make sure to document raspi setup from arduino setup
- Document Schematics (breadboard currently)
- Home-Assistance Integration -- if i can find a way to make this part of my flask site, could open up wemo and other apps
- SENSORS TO BRING UP
  - ULTRASONIC
  - PWM
  - LIGHTS CONTROLS
  - CAMERAS FROM ANALOG -> DIGITAL + LIVE STREAM
  - MICROPHONES + PROCESSING OFFLOAD
- SCHEMATIC FOR EACH COMPONENT

## Main Typology

The system is running with the raspi as the main node, which runs the flask server. Each arduino node will be a seperate project folder, and will need individual setup. 

Raspi = "piALOHA"
- Running Flask Server
- Sending Transmit functions to arduinos
- Recieving Data on the flask backend

Arduino (uno or nano) 
- BED
  - Running main sensor suite
  - IR for LED's
- BATH, BEYOND, and CAVE all run the main sensor suite
- SECURE nodes run secure sensor suite

PC node
- Runs with companion arduino at the moment. Can be used to upload or trigger other events. Main admin + interaction on the system

## Sensor Suites

### Main Sensor Suite
- DHT Humidity / Temperature
- Microphone
- LED / PWM indicator

### Secure Sensor Suite
- Ultra Sonic sensor suite to detect entrance / exit
- Camera if possible on arduino, detecting which direction of motion
- Light / PWM for triggered alarms

## References

[Audio/Visual Lip Reading CNN](https://github.com/astorfi/lip-reading-deeplearning)

[Neural Random Forests](https://arxiv.org/pdf/1604.07143.pdf)

[Network Architecture Guidance](https://stats.stackexchange.com/questions/181/how-to-choose-the-number-of-hidden-layers-and-nodes-in-a-feedforward-neural-netw)

[NRF24LO1+ COMM FROM RASPI TO ARDUINO part 1](https://youtu.be/_68f-yp63ds)

[NRF24LO1+ COMM FROM RASPI TO ARDUINO part 2](https://youtu.be/okdY4fIvysA)

[Raspberry Pi HomeAssistant / Docker / Plex Setup](https://youtu.be/72D3MvPk3Xs)
