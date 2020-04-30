import logging
import time

import adafruit_dht
import paho.mqtt.client as mqtt

logger = logging.getLogger("dht11")

def on_mqtt_connect(topic_prefix):
    def _func(client, *args, **kwargs):
        will_topic = f"{topic_prefix}/connected"
        client.will_set(will_topic, 0, qos=1, retain=True)
        client.publish(will_topic, 1, qos=1, retain=True)
        logger.debug("MQTT Connected.")
    return _func


def on_mqtt_disconnect(topic_prefix):
    def _func(client, *args, **kwargs):
        will_topic = f"{topic_prefix}/connected"
        client.publish(will_topic, 0, qos=1, retain=True)
        logger.debug("MQTT Disconnected")
    return _func()


def loop(
    data_pin,
    broker,
    broker_port,
    topic_prefix,
    protocol=mqtt.MQTTv31,
    cafile=None,
    username=None,
    password=None,
):
    client = mqtt.Client(protocol=protocol)

    if cafile is not None:
        client.tls_set(cafile=cafile)

    if username is not None:
        client.username_pw_set(username, password=password)

    client.on_connect = on_mqtt_connect(topic_prefix)
    client.on_disconnect = on_mqtt_disconnect(topic_prefix)
    client.connect(host=broker, port=broker_port)

    dhtDevice = adafruit_dht.DHT11(data_pin)

    temperature_c, humidity = (None, None)

    try:
        while True:
            try:
                # Print the values to the serial port
                cur_temperature_c = dhtDevice.temperature
                cur_humidity = dhtDevice.humidity

                if cur_temperature_c != temperature_c:
                    temperature_c = cur_temperature_c
                    logger.info(f"Temperature: {temperature_c}")
                    client.publish(f"{topic_prefix}/temperature", temperature_c, qos=1)

                if cur_humidity != humidity:
                    humidity = cur_humidity
                    logger.info(f"Humidity: {humidity}%")
                    client.publish(f"{topic_prefix}/humidity", humidity, qos=1)
            except RuntimeError as error:
                # Errors happen fairly often, DHT's are hard to read, just keep going
                logger.debug(error.args[0])
            time.sleep(2.0)
    except KeyboardInterrupt:
        client.disconnect()
