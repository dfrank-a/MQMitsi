from .message import Message, START_MESSAGE


class HeatPumpController:
    def __init__(self, device: 'mitsubishi.heat_pump.HeatPump'):
        self.device = device
        self.send(START_MESSAGE)

    def send(self, message: 'mitsubishi.message.Message'):
        self.device.write(message)