class Message(bytearray):
    HEADER_LEN = 5

    COMMAND_TYPE = 1
    DATA_LEN = 4
    COMMAND_SUBTYPE = 5

    START_BYTE = 0xFC

    INITIALIZE_SERIAL = 0x5A
    REQUEST_INFO = 0x42

    EXTRA_HEADER = [0x01, 0x30]

    @classmethod
    def valid(cls, message):
        return all([
            len(message.message) == cls.HEADER_LEN + message.data_length,
            cls.checksum(message.message[:-1]) == message.message[-1],
        ])

    @staticmethod
    def checksum(data):
        return 0xFC - (sum(data) & 0xFF)

    @classmethod
    def decode(cls, message):
        if SettingsMessage.is_settings_message(message):
            return SettingsMessage(message)

        if TemperatureMessage.is_temperature_message(message):
            return TemperatureMessage(message)

        return Message(message)

    @classmethod
    def stream_from_device(cls, device):
        while True:
            message = cls.from_stream(device)
            if message:
                yield message

    @classmethod
    def from_stream(cls, device):
        port = device.serial_port
        byte = port.read()
        if ord(byte) == chr(cls.START_BYTE):
            message = bytearray([byte] + port.read(21))
            if cls.valid(message):
                return cls.decode(message)

    @classmethod
    def start_command(cls):
        return Message.build(
            Message.INITIALIZE_SERIAL,
            [0xCA, 0x01]
        )

    @classmethod
    def build(cls, type, payload):
        message = [cls.START_BYTE, type, *cls.EXTRA_HEADER, len(payload), *payload]
        message += [cls.checksum(message)]

        return cls.decode(message)

    @property
    def data_length(self):
        return self[self.DATA_LEN]

    @property
    def type(self):
        return self[self.COMMAND_TYPE]

def message_property(data_position, update_bitmask=None):
    def _getter(self):
        return self[self.HEADER_LEN + data_position]

    _setter = None
    if update_bitmask is not None:
        def _setter(self, value):
            self[self.UPDATE_MASK_INDEX] |= update_bitmask
            self[self.HEADER_LEN + data_position] = value
            self[-1] = Message.checksum(self[:-1])

    return property(
        fget=_getter,
        fset=_setter
    )

class SettingsMessage(Message):
    SEND_UPDATE = 0x41
    SUBTYPE_UPDATE = 0x01
    SETTINGS_INFO = 0x02

    UPDATE_MASK_INDEX = 6

    power = message_property(3, update_bitmask=1)
    mode = message_property(4, update_bitmask=0b10)
    set_point = message_property(5, update_bitmask=0b100)
    fan_speed = message_property(6, update_bitmask=0b1000)
    horizontal_vane = message_property(7, update_bitmask=0b10000)
    vertical_vanes = message_property(10, update_bitmask=0b10000000)

    @classmethod
    def is_settings_message(cls, message):
        msg_type = message[cls.COMMAND_TYPE]
        subtype = message[cls.COMMAND_SUBTYPE]

        return (
            msg_type == cls.SEND_UPDATE
            or (msg_type == cls.REQUEST_INFO and subtype == cls.SETTINGS_INFO)
        )

    @classmethod
    def info_command(cls):
        return cls.build(
            cls.REQUEST_INFO,
            [
                cls.SETTINGS_INFO,
                *([0x00] * 15)
            ]
        )

    @classmethod
    def update_command(cls):
        return cls.build(
            cls.SEND_UPDATE,
            [
                cls.SUBTYPE_UPDATE,
                *([0x00] * 15)
            ]
        )

class TemperatureMessage(Message):
    ROOM_TEMP_INFO = 0x03

    room_temp = message_property(8)

    @classmethod
    def is_temperature_message(cls, message):
        msg_type = message[cls.COMMAND_TYPE]
        subtype = message[cls.COMMAND_SUBTYPE]
        return msg_type == cls.REQUEST_INFO and subtype == cls.ROOM_TEMP_INFO

    @classmethod
    def info_request(cls):
        return cls.build(
            cls.REQUEST_INFO,
            [
                cls.ROOM_TEMP_INFO,
                *([0x00] * 15)
            ]
        )

