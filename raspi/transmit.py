import RPi.GPIO as GPIO
import time, sys
import spidev
from .lib_nrf24 import NRF24

radio = NRF24(GPIO, spidev.SpiDev())
pipes = [[0xE0, 0xE0, 0xF1, 0xF1, 0xE0], [0xF1, 0xF1, 0xF0, 0xF0, 0xE0]]

def init(channel=0x76):
    GPIO.setmode(GPIO.BCM)
    # start the radio and set the ce,csn pin ce= GPIO08, csn= GPIO25
    radio.begin(0, 25)
    radio.setPayloadSize(32)
    radio.setChannel(channel)
    radio.setDataRate(NRF24.BR_1MBPS)
    radio.setPALevel(NRF24.PA_MAX)

    radio.setAutoAck(True)
    radio.enableDynamicPayloads()
    radio.enableAckPayload()

    radio.openWritingPipe(pipes[0])
    radio.printDetails()

def TX(message):
    '''
    input: string of message
    output: 32 bit msg
    '''
    tmp = list(message)
    while len(tmp) < 32:
        tmp.append(0)
    
    radio.write(tmp)

# sendMessage = list("Hi..Arduino UNO")
# while len(sendMessage) < 32:
#     sendMessage.append(0)

if __name__ == "__main__":
    args = sys.argv
    arg_len = int(len(args))
    print(args)

    init()
    try:
        sendMessage = list(args[1])
    except:
        print("didnt find message to send")
        sys.exit()  
 
    radio.write(sendMessage)
    print("Sent the message: {}".format(str(sendMessage)))
    sys.exit()  

    # while True:
    #     # TX
    #     start = time.time()
    #     radio.write(sendMessage)
    #     print("Sent the message: {}".format(sendMessage))

    #     # RX
    #     radio.startListening()
    #     while not radio.available(0):
    #         time.sleep(1/100)
    #         if time.time() - start > 2:
    #             print("Timed out.")
    #             break
    #     radio.stopListening()
