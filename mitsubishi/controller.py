import asyncio
import logging
import serial

from pprint import pformat

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

    def __init__(self, serial_port,
                 temp_refresh_rate=10,
                 settings_refresh_rate=2,
                 operation_status_refresh_rate=2
             ):
        self.device = serial.Serial(
            port=serial_port, baudrate=2400, parity=serial.PARITY_EVEN, timeout=0
        )
        self.device.write(Message.start_command())
        self.device_queue = None
        self.temp_refresh_rate = temp_refresh_rate
        self.settings_refresh_rate = settings_refresh_rate
        self.operation_status_refresh_rate = operation_status_refresh_rate

        self.room_temp = None
        self.operating = None
        self.compressor_frequency = None

        self.current_pump_state = {}

    async def queue_request_message(self, message, refresh_rate):
        while True:
            logger.debug(f"Sending {repr(message)}")
            await self.device_queue.put(message)
            await asyncio.sleep(refresh_rate)

    async def submit_messages(self):
        while True:
            try:
                message = self.device_queue.get_nowait()
                logger.debug(f"Sending {repr(message)}")
                self.device.write(message)
                self.device_queue.task_done()
            except asyncio.QueueEmpty:
                pass
            await asyncio.sleep(0)

    async def read_device_stream(self):
        while True:
            message = Message.from_stream(self.device)
            if message is not None:
                if isinstance(message, TemperatureMessage):
                    self.debug(bytearray(message))
                    room_temp = message.room_temp
                    if self.room_temp != room_temp:
                        logger.info(f"Room Temp: {room_temp}")
                        self.room_temp = room_temp
                elif isinstance(message, OperationStatusMessage):
                    if self.operating != message.operating:
                        logger.info(f"Pump: {message.operating}")
                        self.operating = message.operating
                    if self.compressor_frequency != message.compressor_frequency:
                        logger.info(f"Compressor frequency: {message.compressor_frequency}")
                        self.compressor_frequency = message.compressor_frequency
                elif isinstance(message, SettingsMessage):
                    changes = {
                        attr: getattr(message, attr)
                        for attr in self.SETTINGS_ATTRS
                        if self.current_pump_state.get(attr) != getattr(message, attr)
                    }
                    if changes:
                        self.current_pump_state.update(changes)
                        logger.info(pformat(self.current_pump_state))
                logger.debug(message)
            await asyncio.sleep(1)

    def loop(self):
        async def _loop():
            self.device_queue = asyncio.Queue()
            await asyncio.gather(
                *[
                    asyncio.create_task(task)
                    for task in [
                        self.queue_request_message(
                            TemperatureMessage.info_request(),
                            self.temp_refresh_rate
                        ),
                        self.queue_request_message(
                            SettingsMessage.info_request(),
                            self.settings_refresh_rate
                        ),
                        self.queue_request_message(
                            OperationStatusMessage.info_request(),
                            self.operation_status_refresh_rate
                        ),
                        self.submit_messages(),
                        self.read_device_stream(),
                    ]
                ]
            )

        asyncio.run(_loop())
