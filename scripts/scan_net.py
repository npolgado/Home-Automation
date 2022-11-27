import os, sys, re

devices = []
for device in os.popen('arp -a'):
    print(device)
    for i in re.findall("\([^)]+\)", device):
        devices.append(str(i)[1:-1])

print(devices)
