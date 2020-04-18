import logging
import time

import adafruit_dht
import board
import paho.mqtt.client as mqtt

logger = logging.getLogger("dh11")
handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter('%(asctime)s: %(message)s')
)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def on_mqtt_connect(topic_prefix):
    def _func(client, *args, **kwargs):
        will_topic = f"{topic_prefix}/connected"
        client.will_set(will_topic, 0, qos=1, retain=True)
        client.publish(will_topic, 1, qos=1, retain=True)
        logger.info("MQTT Connected.")

    return _func


def on_mqtt_disconnect(topic_prefix):
    def _func(client, *args, **kwargs):
        will_topic = f"{topic_prefix}/connected"
        client.publish(will_topic, 0, qos=1, retain=True)


def __main__(
    broker="127.0.0.1", broker_port=1883, topic_prefix="grow_room/sensors/dh11"
):
    client = mqtt.Client(protocol=mqtt.MQTTv31)
    client.on_connect = on_mqtt_connect(topic_prefix)
    client.on_disconnect = on_mqtt_disconnect(topic_prefix)
    client.connect(host=broker, port=broker_port)

    dhtDevice = adafruit_dht.DHT11(board.D4)

    temperature_c, humidity = (None, None)
    while True:
        try:
            # Print the values to the serial port
            cur_temperature_c = dhtDevice.temperature
            cur_humidity = dhtDevice.humidity

            if cur_temperature_c != temperature_c:
                temperature_c = cur_temperature_c
                temperature_f = round(cur_temperature_c * (9 / 5) + 32, 2)
                logger.info(f"Temp: {temperature_f:.1f} F / {temperature_c:.1f} C")
                client.publish(f"{topic_prefix}/temperature", temperature_c, qos=1)

            if cur_humidity != humidity:
                humidity = cur_humidity
                logger.info(f"Humidity: {humidity}%")
                client.publish(f"{topic_prefix}/humidity", humidity, qos=1)
        except RuntimeError as error:
            # Errors happen fairly often, DHT's are hard to read, just keep going
            print(error.args[0])
        time.sleep(2.0)


if __name__ == "__main__":
    __main__()
