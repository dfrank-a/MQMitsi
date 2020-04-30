import atexit
import logging
import time
import board
import adafruit_dht
import paho.mqtt.client as mqtt

from threading import Thread

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
    return _func

class DHT11:
    def __init__(
        self,
        data_pin,
        broker,
        broker_port,
        topic_prefix,
        protocol=mqtt.MQTTv31,
        username=None,
        password=None,
    ):
        client = mqtt.Client(protocol=protocol)

        if username is not None:
            client.username_pw_set(username, password=password)

        client.on_connect = on_mqtt_connect(topic_prefix)
        client.on_disconnect = on_mqtt_disconnect(topic_prefix)
        client.connect(host=broker, port=broker_port)

        self.mqtt_client=client
        self.device = adafruit_dht.DHT11(getattr(board, data_pin))
        self.running = None

    def _poll_status(self):
        temperature_c, humidity = (None, None)
        while self.running:
            try:
                # Print the values to the serial port
                cur_temperature_c = self.device.temperature
                cur_humidity = self.device.humidity

                if cur_temperature_c != temperature_c:
                    temperature_c = cur_temperature_c
                    logger.info(f"Temperature: {temperature_c}")
                    self.mqtt_client.publish(f"{topic_prefix}/temperature", temperature_c, qos=1)

                if cur_humidity != humidity:
                    humidity = cur_humidity
                    logger.info(f"Humidity: {humidity}%")
                    self.mqtt_client.publish(f"{topic_prefix}/humidity", humidity, qos=1)
            except RuntimeError as error:
                # Errors happen fairly often, DHT's are hard to read, just keep going
                logger.debug(error.args[0])
            time.sleep(2.0)

    def start(self):
        self.mqtt_client.loop_start()
        self.running = True
        Thread(target=self._poll_status).start()
        atexit.register(self._loop_stop)

    def _loop_stop(self):
        self.running = False
        self.mqtt_client.loop_stop()
