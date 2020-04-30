import logging
import os

from mitsubishi import HeatPumpController
from sensors.dht11 import DHT11

logger = logging.getLogger('')
handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter('%(asctime)s [%(levelname)s %(name)s] %(message)s')
)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

env = os.environ

HeatPumpController(
    serial_port=env["SERIAL_PORT"],
    broker=env["BROKER_URL"],
    broker_port=int(env["BROKER_PORT"]),
    username=env["MQTT_USERNAME"],
    password=env["MQTT_PASSWORD"],
    topic_prefix="grow_room/heat_pump"
).start()

DHT11(
    data_pin=env["DHT11_PIN"],
    broker=env["BROKER_URL"],
    broker_port=int(env["BROKER_PORT"]),
    username=env["MQTT_USERNAME"],
    password=env["MQTT_PASSWORD"],
    topic_prefix="grow_room/DHT11"
).start()

