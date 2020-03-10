import logging

from .lookup import (
    FAN_LOOKUP,
    HORIZONTAL_VANE_LOOKUP,
    MODE_LOOKUP,
    POWER_LOOKUP,
    ROOM_TEMP_LOOKUP,
    SET_POINT_LOOKUP,
    VERTICAL_VANE_LOOKUP,
)

logger = logging.getLogger(__name__)

class Message(bytearray):
    HEADER_LEN = 5

    COMMAND_TYPE = 1
    DATA_LEN = 4
    COMMAND_SUBTYPE = 5

    START_BYTE = 0xFC

    INITIALIZE_SERIAL = 0x5A
    REQUEST_INFO = 0x42
    RESPONSE_INFO = 0x62

    EXTRA_HEADER = [0x01, 0x30]

    @classmethod
    def valid(cls, message):
        return all([
            len(message) == cls.HEADER_LEN + message[cls.DATA_LEN] + 1,
            cls.checksum(message[:-1]) == message[-1],
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
    def from_stream(cls, device):
        byte = device.read()
        logger.debug(f'Got byte {byte}')
        if byte and ord(byte) == cls.START_BYTE:
            device.timeout = None
            header = byte + device.read(cls.HEADER_LEN - 1)
            data_len = header[cls.DATA_LEN]
            message = header + device.read(data_len + 1)
            device.timeout = 0
            if cls.valid(message):
                return cls.decode(message)
        return None

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

    @property
    def subtype(self):
        return self[self.HEADER_LEN]

    def __str__(self):
        return " ".join([
            f"{self[i]:02x}" if i < len(self) else "  "
            for i in range(22)
        ]) + f" len={self.data_length:03} type={self.type:02x}"

def message_property(data_position, update_bitmask=None, lookup_table=tuple()):

    get_lookup = dict(lookup_table)

    if update_bitmask is not None:
        def _getter(self):
            if self.subtype == self.SETTINGS_INFO or self[self.UPDATE_MASK_INDEX] & update_bitmask:
                value = self[self.HEADER_LEN + data_position]
                return get_lookup.get(value, value)
            return None
    else:
        def _getter(self):
            value = self[self.HEADER_LEN + data_position]
            return get_lookup.get(value, value)

    _setter = None
    if update_bitmask is not None:
        set_lookup = dict((j, i) for i, j in lookup_table)
        def _setter(self, value):
            self[self.UPDATE_MASK_INDEX] |= update_bitmask
            self[self.HEADER_LEN + data_position] = set_lookup[value]
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

    power = message_property(3, update_bitmask=1, lookup_table=POWER_LOOKUP)
    mode = message_property(4, update_bitmask=0b10, lookup_table=MODE_LOOKUP)
    set_point = message_property(5, update_bitmask=0b100, lookup_table=SET_POINT_LOOKUP)
    fan_speed = message_property(6, update_bitmask=0b1000, lookup_table=FAN_LOOKUP)
    vertical_vane = message_property(7, update_bitmask=0b10000, lookup_table=VERTICAL_VANE_LOOKUP)
    horizontal_vane = message_property(10, update_bitmask=0b10000000, lookup_table=HORIZONTAL_VANE_LOOKUP)

    @classmethod
    def is_settings_message(cls, message):
        msg_type = message[cls.COMMAND_TYPE]
        subtype = message[cls.COMMAND_SUBTYPE]

        return (
            msg_type == cls.SEND_UPDATE
            or (msg_type in {cls.REQUEST_INFO, cls.RESPONSE_INFO} and subtype == cls.SETTINGS_INFO)
        )

    @classmethod
    def info_request(cls):
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

    def __str__(self):
        if self.subtype == self.SUBTYPE_UPDATE:
            return " ".join([
                super().__str__(),
                *[
                    f.format(v)
                    for f, v in [
                        ("{:3s}", self.power),
                        ("{:4s}", self.mode),
                        ("Fan {:5s}", self.fan_speed),
                        ("H Vane {:5s}", self.horizontal_vane),
                        ("V Vane {:5s}", self.vertical_vane)
                    ]
                    if v is not None
                ]
            ])
        else:
            return " ".join([
                    super().__str__(),
                    f"{self.power:3s}",
                    f"MODE:{self.mode:4s}",
                    f"{self.set_point:5s} ºC"
                    f"Fan: {self.fan_speed:5s}",
                    f"H vane: {self.horizontal_vane:5s}",
                    f"V vane: {self.vertical_vane:5s}"
            ])

    def __eq__(self, other):
        return all([
            a == b
            for a, b in [
                (self.power, other.power),
                (self.mode, other.mode),
                (self.set_point, other.set_point),
                (self.fan_speed, other.fan_speed),
                (self.vertical_vane, other.vertical_vane),
                (self.horizontal_vane, other.horizontal_vane)
            ]
            if not (a is None or b is None)
        ])

class TemperatureMessage(Message):
    ROOM_TEMP_INFO = 0x03

    room_temp = message_property(3, lookup_table=ROOM_TEMP_LOOKUP)

    # this seems to change, in auto mode,
    # b1 when temp was at set point, b2 when over...maybe?
    unknown_1 = message_property(6)

    @classmethod
    def is_temperature_message(cls, message):
        msg_type = message[cls.COMMAND_TYPE]
        subtype = message[cls.COMMAND_SUBTYPE]
        return msg_type in {cls.REQUEST_INFO, cls.RESPONSE_INFO} and subtype == cls.ROOM_TEMP_INFO

    @classmethod
    def info_request(cls):
        return cls.build(
            cls.REQUEST_INFO,
            [
                cls.ROOM_TEMP_INFO,
                *([0x00] * 15)
            ]
        )

    def __str__(self):
        return ' '.join([
                super().__str__(),
                f"Room: {self.room_temp} ºC",
                f"???: {self.unknown_1}"
        ])