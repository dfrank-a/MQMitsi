import logging

from .message import Message, SettingsMessage, TemperatureMessage

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter('%(asctime)s: %(message)s')
)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class HeatPumpController:
    def __init__(self, device):
        self.device = device
        self.send(Message.start_command())
        self.message_stream = Message.stream_from_device(self.device)

    def loop(self):
        for message in self.message_stream:
            logger.debug(repr(message))

            if isinstance(message, SettingsMessage):
                self.device.write(TemperatureMessage.info_request())
            elif isinstance(message, TemperatureMessage):
                self.device.write(SettingsMessage.info_request())
            else:
                self.device.write(TemperatureMessage.info_request())

