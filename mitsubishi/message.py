
def message_property(data_position, control_packet_mask):
    def _getter(self):
        return self.message[self.HEADER_LEN + data_position]

    def _setter(self, value):
        self.message[self.CONTROL_BYTE_INDEX] |= control_packet_mask
        self.message[self.HEADER_LEN + data_position] = value

    return property(
        fget=_getter,
        fset=_setter
    )


class Message:
    HEADER_LEN = 6
    DATA_LEN_INDEX = 4
    MESSAGE_TYPE_INDEX = 1
    CONTROL_BYTE_INDEX = 6

    START_BYTE = chr(0xFC)

    #Position 1: Message Types
    START_CONNECTION = chr(0x5A)
    REQUEST_INFO = chr(0x42)
    SEND_UPDATE = chr(0x41)

    SETTINGS_INFO = chr(0x02)
    ROOM_TEMP_INFO = chr(0x03)

    @classmethod
    def valid(cls, message):
        return all([
            len(message.message) == cls.HEADER_LEN + message.data_length,
            cls.checksum(message.message[:-1]) == message.message[-1],
        ])

    @staticmethod
    def checksum(cls, data):
        return 0xFC - (sum(data) & 0xFF)

    @classmethod
    def stream_from_device(cls, device: 'mitsubishi.heat_pump.HeatPump'):
        while True:
            message = cls.from_stream(device)
            if message:
                yield message

    @classmethod
    def from_stream(cls, device: 'mitsubishi.heat_pump.HeatPump'):
        port = device.serial_port
        byte = port.read()
        if byte == cls.START_BYTE:
            header = [byte] + port.read(cls.HEADER_LEN - 1)
            data_len = ord(header[cls.DATA_LEN_INDEX])
            data = port.read(data_len)

            message = Message(header + data)

            if Message.valid(message):
                return message

    def __init__(self, bytes=None):
        if bytes is not None:
            self.message = bytes

    def __str__(self):
        return bytes(self.message, encoding='ascii')

    @property
    def data_length(self):
        return ord(bytes[self.DATA_LEN_INDEX])

    @property
    def type(self):
        return self.message[self.MESSAGE_TYPE_INDEX]

    power = message_property(3, 1)
    mode = message_property(4, 0b10)
    set_point = message_property(5, 0b100)
    fan_speed = message_property(6, 0b1000)
    horizontal_vane = message_property(7, 0b10000)
    vertical_vanes = message_property(10, 0b10000000)