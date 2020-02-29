from .message import Message


class HeatPumpController:
    def __init__(self, device: 'mitsubishi.heat_pump.HeatPump'):
        self.device = device
        self.send(

        )

    def send(self, message: 'mitsubishi.message.Message'):
        self.device.write(message)