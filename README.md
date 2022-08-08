<h1 align="center">HOME AUTOMATION</h1>

> the code base and organized notes for a home automation system using `arduino`, `raspberry pi`, and hopefully some `more fun`

## How To Install:

## Quickstart:

## TO DO:
-Rasp Pi HA / Plex Setup
-HA SETUP WITH CUSTOM NODES
-Pi Base node logic
  -Special Protocol (Similar to AUV)
  -Command / Telemetry / ACK / CRC / UPDATES?? / WEB UPDATED? 
-NRF24 networking based on NRF24L01+ and libraries

## IC Core Component Requirements
  * BED NODE:
      * IR TX
      * NRF COMM
      * MICROPHONE
      * PWM SPEAKER
  * CAVE NODE:
      * MICROPHONE
      * TEMPURATURE
      * NRF COMM
      * PWM SPEAKER
  * BATH NODE:
      * MICROPHOEN
      * NRF COMM
      * PWM SPEAKER
  * THEATER NODE:
      * MICROPHONE
      * PWM SPEAKER / LED STATUS
  * SECURE NODES:
      * ULTRASONIC
      * MICROPHONE
      * CAMERA 
  * ALL IC's HAVE SHORE POWER access and are modular around the specific room


## References

Audio/Visual Lip Reading CNN:
  * https://github.com/astorfi/lip-reading-deeplearning

Neural Random Forests:
  * https://arxiv.org/pdf/1604.07143.pdf

Network Architecture Guidance:
  * https://stats.stackexchange.com/questions/181/how-to-choose-the-number-of-hidden-layers-and-nodes-in-a-feedforward-neural-netw
  
NRF24LO1+ Network Guidance (ARDUINO): 
  * https://youtu.be/xb7psLhKTMA

NRF24L01+ with the Raspberry Pi:
  * https://youtu.be/6KJGsmSZnzg

NRF24L01+ Long Range Video Feed (PI):
  * https://youtu.be/9N1uRcvZzq4

Raspberry Pi HomeAssistant / Docker / Plex Setup:
  * https://youtu.be/72D3MvPk3Xs
