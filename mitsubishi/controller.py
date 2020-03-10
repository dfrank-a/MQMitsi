import asyncio
import logging
import serial

from pprint import pformat

from .message import Message, SettingsMessage, TemperatureMessage

logger = logging.getLogger(__name__)

class HeatPumpController:
    SETTINGS_ATTRS = [
        'power', 'mode', 'set_point', 'fan_speed',
        'vertical_vane', 'horizontal_vane'
    ]

    def __init__(self, serial_port, temp_refresh_rate=10, settings_refresh_rate=2):
        self.device = serial.Serial(
            port=serial_port,
            baudrate=2400,
            parity=serial.PARITY_EVEN,
            timeout=0
        )
        self.device.write(Message.start_command())
        self.queue = None
        self.temp_refresh_rate = temp_refresh_rate
        self.settings_refresh_rate = settings_refresh_rate

        self.room_temp = None
        self.mystery_byte = None

        self.current_pump_state = {}

    async def request_temperature_update(self):
        TEMP_REQUEST = TemperatureMessage.info_request()
        while True:
            logger.debug("Requesting temp update")
            await self.queue.put(TEMP_REQUEST)
            await asyncio.sleep(self.temp_refresh_rate)

    async def request_settings_update(self):
        SETTINGS_REQUEST = SettingsMessage.info_request()
        while True:
            logger.debug("Requesting settings update")
            await self.queue.put(SETTINGS_REQUEST)
            await asyncio.sleep(self.settings_refresh_rate)

    async def submit_messages(self):
        while True:
            try:
                message = self.queue.get_nowait()
                logger.debug("Sending message")
                self.device.write(message)
                self.queue.task_done()
            except asyncio.QueueEmpty:
                pass
            await asyncio.sleep(0)

    async def read_device_stream(self):
        while True:
            logger.debug("Checking messages")
            message = Message.from_stream(self.device)
            if message is not None:
                if isinstance(message, TemperatureMessage):
                    room_temp = message.room_temp
                    mystery_byte = message.mystery_byte

                    if self.room_temp != room_temp:
                        logger.info(f"Room Temp: {room_temp}")
                        self.room_temp = room_temp

                    if self.mystery_byte != mystery_byte:
                        logger.info(f"Mystery Temp Byte: {mystery_byte}")
                        self.mystery_byte = mystery_byte
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
            self.queue = asyncio.Queue()
            await asyncio.gather(*[
                asyncio.create_task(task)
                for task in [
                    self.request_settings_update(),
                    self.request_temperature_update(),
                    self.submit_messages(),
                    self.read_device_stream(),
                ]
            ])
        asyncio.run(_loop())