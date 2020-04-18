import logging
import serial

from pprint import pformat
from random import random
from queue import Queue, Empty as QueueEmpty
from time import sleep
from threading import Thread

import paho.mqtt.client as mqtt

from .message import (
    Message,
    SettingsMessage,
    TemperatureMessage,
    OperationStatusMessage,
)

logger = logging.getLogger(__name__)


class HeatPumpController:
    SETTINGS_ATTRS = [
        "power",
        "mode",
        "set_point",
        "fan_speed",
        "vertical_vane",
        "horizontal_vane",
    ]

    def __init__(self,
                 serial_port='/dev/serial0',
                 broker='127.0.0.1',
                 broker_port=1883,
                 topic_prefix='heat_pump',
                 temp_refresh_rate=10,
                 settings_refresh_rate=2,
                 operation_status_refresh_rate=2
             ):

        self.topic_prefix = topic_prefix
        self.broker = broker
        self.broker_port = broker_port
        self.client = mqtt.Client(protocol=mqtt.MQTTv31)
        self.client.on_connect = self.on_mqtt_connect
        self.client.on_message = self.on_mqtt_message

        self.device = serial.Serial(
            port=serial_port, baudrate=2400, parity=serial.PARITY_EVEN
        )

        self.device_queue = Queue()
        self.temp_refresh_rate = temp_refresh_rate
        self.settings_refresh_rate = settings_refresh_rate
        self.operation_status_refresh_rate = operation_status_refresh_rate

        self.room_temp = None
        self.operating = None
        self.compressor_frequency = None

        self.current_pump_state = {}

    def queue_request_message(self, message, refresh_rate):
        while True:
            logger.debug(f"Queued {repr(message)}")
            self.device_queue.put(message)
            sleep(refresh_rate + random() / 10)

    def process_messages(self):
        while True:
            try:
                message = self.device_queue.get()
                self.device.write(message)
                logger.debug(f"Sent {repr(message)}")
                self.read_device_stream()
                self.device_queue.task_done()
            except QueueEmpty:
                pass
            sleep(0)

    def read_device_stream(self):
        response = Message.from_stream(self.device)
        if response is not None:
            logger.debug(f"Received {repr(response)}")
            if isinstance(response, TemperatureMessage):
                room_temp = response.room_temp
                if self.room_temp != room_temp:
                    logger.info(f"Room Temp: {room_temp}")
                    self.room_temp = room_temp
                    self.client.publish(
                        topic=f"{self.topic_prefix}/room_temp",
                        payload=self.room_temp,
                        qos=1,
                        retain=True
                    )
            elif isinstance(response, OperationStatusMessage):
                if self.operating != response.operating:
                    logger.info(f"Pump: {response.operating}")
                    self.operating = response.operating
                    self.client.publish(
                        topic=f"{self.topic_prefix}/compressor/state",
                        payload=self.operating,
                        qos=1,
                        retain=True
                    )
                if self.compressor_frequency != response.compressor_frequency:
                    self.compressor_frequency = response.compressor_frequency
                    self.client.publish(
                        topic=f"{self.topic_prefix}/compressor/frequency",
                        payload=self.compressor_frequency,
                        qos=1,
                        retain=True
                    )
            elif isinstance(response, SettingsMessage):
                changes = {
                    attr: getattr(response, attr)
                    for attr in self.SETTINGS_ATTRS
                    if self.current_pump_state.get(attr) != getattr(response, attr)
                }
                if changes:
                    self.current_pump_state.update(changes)
                    logger.info(pformat(self.current_pump_state))
                    for attr, value in changes.items():
                        self.client.publish(
                            topic=f"{self.topic_prefix}/settings/{attr}",
                            payload=value,
                            qos=1,
                            retain=True
                        )

    def on_mqtt_connect(self, client: mqtt.Client, *args, **kwargs):
        will_topic = f'{self.topic_prefix}/connected'
        client.will_set(will_topic, 0, qos=1, retain=True)
        client.publish(will_topic, 1, qos=1, retain=True)
        client.subscribe(f"{self.topic_prefix}/update/#")
        logger.info("MQTT Connected.")

    def on_mqtt_message(self, _, __, msg):
        logger.info(f"MQTT Message: {msg.topic}: {msg.payload}")

        attribute = msg.topic.split('/')[-1]
        if attribute in self.SETTINGS_ATTRS:
            value = msg.payload.decode('utf-8')
            if attribute == 'set_point':
                value = float(value)

            update_command = SettingsMessage.update_command()
            setattr(update_command, attribute, value)

            logger.info(f"Submitting update of {attribute} to {value}")
            self.device_queue.put(update_command)

    def loop(self):
        self.device_queue.put(Message.start_command())
        Thread(target=self.process_messages).start()

        periodic_checks = [
            (TemperatureMessage.info_request(), self.temp_refresh_rate),
            (SettingsMessage.info_request(), self.settings_refresh_rate),
            (OperationStatusMessage.info_request(), self.operation_status_refresh_rate)
        ]
        for periodic in periodic_checks:
            Thread(
                target=self.queue_request_message,
                args=periodic
            ).start()

        self.client.connect(host=self.broker, port=self.broker_port)
        self.client.loop_forever()