import logging

from mitsubishi import HeatPumpController

logger = logging.getLogger('')
handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter('%(asctime)s: %(message)s')
)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


HeatPumpController('/dev/serial0').loop()
