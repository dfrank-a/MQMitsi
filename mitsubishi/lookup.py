FAN_LOOKUP = (
    (0x00, "AUTO"),
    (0x01, "QUIET"),
    (0x02, "1"),
    (0x03, "2"),
    (0x05, "3"),
    (0x06, "4"),
)

HORIZONTAL_VANE_LOOKUP = (
    (0x00, "NA"),
    (0x01, "<<"),
    (0x02, "<"),
    (0x03, "|"),
    (0x04, ">"),
    (0x05, ">>"),
    (0x08, "<>"),
    (0x0C, "SWING"),
)

MODE_LOOKUP = (
    (0x01, "HEAT"),
    (0x02, "DRY"),
    (0x03, "COOL"),
    (0x07, "FAN"),
    (0x08, "AUTO"),
)

POWER_LOOKUP = (
    (0x00, "OFF"),
    (0x01, "ON"),
)

ROOM_TEMP_LOOKUP = (
    (0x00, 10),
    (0x01, 11),
    (0x02, 12),
    (0x03, 13),
    (0x04, 14),
    (0x05, 15),
    (0x06, 16),
    (0x07, 17),
    (0x08, 18),
    (0x09, 19),
    (0x0A, 20),
    (0x0B, 21),
    (0x0C, 22),
    (0x0D, 23),
    (0x0E, 24),
    (0x0F, 25),
    (0x10, 26),
    (0x11, 27),
    (0x12, 28),
    (0x13, 29),
    (0x14, 30),
    (0x15, 31),
    (0x16, 32),
    (0x17, 33),
    (0x18, 34),
    (0x19, 35),
    (0x1A, 36),
    (0x1B, 37),
    (0x1C, 38),
    (0x1D, 39),
    (0x1E, 40),
    (0x1F, 41),
)

SET_POINT_LOOKUP = (
    (0x00, 31),
    (0x01, 30),
    (0x02, 29),
    (0x03, 28),
    (0x04, 27),
    (0x05, 26),
    (0x06, 25),
    (0x07, 24),
    (0x08, 23),
    (0x09, 22),
    (0x0A, 21),
    (0x0B, 20),
    (0x0C, 19),
    (0x0D, 18),
    (0x0E, 17),
    (0x0F, 16),
    (0x1F, 16.5),
    (0x1E, 17.5),
    (0x1D, 18.5),
    (0x1C, 19.5),
    (0x1B, 20.5),
    (0x1A, 21.5),
    (0x19, 22.5),
    (0x18, 23.5),
    (0x17, 24.5),
    (0x16, 25.5),
    (0x15, 26.5),
    (0x14, 27.5),
    (0x13, 28.5),
    (0x12, 29.5),
    (0x11, 30.5),
    (0x10, 31.5),
)

VERTICAL_VANE_LOOKUP = (
    (0x00, "AUTO"),
    (0x01, "1"),
    (0x02, "2"),
    (0x03, "3"),
    (0x04, "4"),
    (0x05, "5"),
    (0x07, "SWING"),
)

TIMER_MODE = (
    (0x00, "NONE"),
    (0x01, "OFF"),
    (0x02, "ON"),
    (0x03, "BOTH"),
)

TIMER_MINUTES_INCREMENT = 10