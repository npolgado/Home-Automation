import logging
import paho.mqtt.client as mqtt

IP_TX2 = "192.168.0.43"
IP_ALOHA = "192.168.0.17"
RATE = 0.2

logging.basicConfig(level=logging.DEBUG)

def on_log(client, userdata, paho_log_level, messages):
    if paho_log_level == mqtt.LogLevel.MQTT_LOG_ERR:
        try: print([message for message in messages])
        except: print(messages)

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.enable_logger()
mqttc.on_log = on_log

mqttc.connect("mqtt.eclipseprojects.io", 1883, 60)
mqttc.loop_start()

"""
while run:
    if need_read:
        mqttc.loop_read()
    if need_write:
        mqttc.loop_write()
    mqttc.loop_misc()

    if not need_read and not need_write:
        # But don't wait more than few seconds, loop_misc() need to be called regularly
        wait_for_change_in_need_read_or_write()
    updated_need_read_and_write()
"""