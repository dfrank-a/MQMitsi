import asyncio
import logging
import serial

from .message import Message, SettingsMessage, TemperatureMessage

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter('%(asctime)s: %(message)s')
)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class HeatPumpController:
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

    async def request_temperature_update(self):
        TEMP_REQUEST = TemperatureMessage.info_request()
        while True:
            await self.queue.put(TEMP_REQUEST)
            await asyncio.sleep(self.temp_refresh_rate)

    async def request_settings_update(self):
        SETTINGS_REQUEST = SettingsMessage.info_request()
        while True:
            await self.queue.put(SETTINGS_REQUEST)
            await asyncio.sleep(self.temp_refresh_rate)

    async def submit_messages(self):
        while True:
            message = await self.queue.get()
            self.device.write(message)
            self.queue.task_done()

    async def read_device_stream(self):
        while True:
            message = Message.from_stream(self.device)
            if message is not None:
                logger.debug(repr(message))
            await asyncio.sleep(0.1)

    def loop(self):
        async def _loop():
            self.queue = asyncio.Queue()
            await asyncio.gather(
                self.read_device_stream(),
                self.submit_messages(),
                self.request_settings_update(),
                self.request_temperature_update()
            )
        asyncio.run(_loop())