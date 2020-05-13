import logging.config
import os

from growroom.mitsubishi import HeatPumpController
from growroom.sensors import DHT11

logger = logging.getLogger('')
handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter('%(asctime)s [%(levelname)s %(name)s] %(message)s')
)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def main():
    env = os.environ

    logging_config = env.get("LOGGING_CONFIG_FILE")
    if logging_config:
        logging.config.fileConfig(logging_config)

    HeatPumpController(
        serial_port=env["SERIAL_PORT"],
        broker=env["BROKER_URL"],
        broker_port=int(env["BROKER_PORT"]),
        username=env["MQTT_USERNAME"],
        password=env["MQTT_PASSWORD"],
        ca_certs=env["CERTIFICATE_AUTHORITY"],
        topic_prefix="grow_room/heat_pump"
    ).start()

    DHT11(
        data_pin=env["DHT11_PIN"],
        broker=env["BROKER_URL"],
        broker_port=int(env["BROKER_PORT"]),
        username=env["MQTT_USERNAME"],
        password=env["MQTT_PASSWORD"],
        ca_certs=env["CERTIFICATE_AUTHORITY"],
        topic_prefix="grow_room/DHT11"
    ).start()
