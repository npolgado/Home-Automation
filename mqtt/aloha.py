import time
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import paho.mqtt.subscribe as subscribe
from paho.mqtt.enums import MQTTProtocolVersion
import random
import os
import sys

RATE = 0.2
IP_TX2 = os.environ.get("IP_TX2")

def on_message_print(client, userdata, message):
    print("%s %s" % (message.topic, message.payload))
    userdata["message_count"] += 1
    if userdata["message_count"] >= 5:
        # it's possible to stop the program by disconnecting
        client.disconnect()

def on_publish(client, userdata, mid, reason_code, properties):
    # reason_code and properties will only be present in MQTTv5. It's always unset in MQTTv3
    try:
        userdata.remove(mid)
    except KeyError:
        print("on_publish() is called with a mid not present in unacked_publish")
        print("This is due to an unavoidable race-condition:")
        print("* publish() return the mid of the message sent.")
        print("* mid from publish() is added to unacked_publish by the main thread")
        print("* on_publish() is called by the loop_start thread")
        print("While unlikely (because on_publish() will be called after a network round-trip),")
        print(" this is a race-condition that COULD happen")
        print("")
        print("The best solution to avoid race-condition is using the msg_info from publish()")
        print("We could also try using a list of acknowledged mid rather than removing from pending list,")
        print("but remember that mid could be re-used !")

unacked_publish = set()
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_publish = on_publish
client.user_data_set(unacked_publish)
client.connect(IP_TX2)
client.loop_start()

# subscribe.callback(on_message_print, "paho/test/topic", hostname=IP_TX2, userdata={"message_count": 0})

while True:
    # generate a random string to send for each client
    # random_string_tx2 = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=20))

    temp = os.popen("/opt/vc/bin/vcgencmd measure_temp").read().split("=")[1][:-3]
    # print(temp)

    free_mem = os.popen("free -m").read().split("\n")[1].split()[3]
    # print(free_mem)

    free_storage = os.popen("df -h /").read().split("\n")[1].split()[3] 
    # print(free_storage) 

    msgs = [
        ('/sys/temp', temp, 1, False),
        ('/sys/mem', free_mem, 1, False),
        ('/sys/storage', free_storage, 1, False)
    ]
    publish.multiple(msgs, hostname='localhost', protocol=MQTTProtocolVersion.MQTTv5)

    # msg_temp = client.publish('/sys/temp', temp, qos=1)
    # unacked_publish.add(msg_temp.mid)

    # msg_freem = client.publish('/sys/mem', temp, qos=1)
    # unacked_publish.add(msg_freem.mid)

    # msg_storage = client.publish('/sys/storage', temp, qos=1)
    # unacked_publish.add(msg_storage.mid)

    # # Wait for all message to be published
    # while len(unacked_publish):
    #     time.sleep(0.1)

    # # Due to race-condition described above, the following way to wait for all publish is safer
    # msg_temp.wait_for_publish()
    # msg_freem.wait_for_publish()
    # msg_storage.wait_for_publish()

    print("\nSENT!\n")

    time.sleep(RATE)

client.loop_stop()
client.disconnect()
