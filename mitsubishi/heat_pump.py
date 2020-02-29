import serial


class HeatPump:
    def __init__(self, serial_port: str):
        self.serial_port = serial.Serial(
            port=serial_port,
            baudrate=2400,
            parity=serial.PARITY_EVEN,
        )

    def write(self, message):
        self.serial_port.write(message)