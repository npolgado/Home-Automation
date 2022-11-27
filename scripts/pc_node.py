import serial
import time
import sys
import urllib
import urllib.request

input=1
try:    
    with serial.Serial('COM4', 9600) as ser:
        while 1 :
            input = ser.readline()
            print(input)
            try:
                vals = str(input).split("-")
                addr = "http://192.168.1.141:5000/log/PC/" + str(vals[0])[2:] + "-" + str(vals[1]) + "-" + str(vals[2])[:-5] + "-0-0-0-0-0"
                print(f"sending {addr}")
                url = urllib.request.urlopen(addr)
                print(f"result code = {url.getcode()}")
            except Exception:
                print("Error")
                pass
except KeyboardInterrupt:
    ser.close()
    sys.exit(1)