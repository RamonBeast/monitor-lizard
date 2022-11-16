import time

try:
    from smbus2 import SMBus
except ImportError:
    from smbus import SMBus
from bme280 import BME280

bus = SMBus(1)
bme280 = BME280(i2c_dev=bus)

# Dump calibration data
for key in dir(bme280.calibration):
    if key.startswith('dig_'):
        value = getattr(bme280.calibration, key)
        print('{} = {}'.format(key, value))

# Dump sensor's readings ever second
while True:
    temperature = bme280.get_temperature()
    pressure = bme280.get_pressure()
    humidity = bme280.get_humidity()
    print('{:05.2f}*C {:05.2f}hPa {:05.2f}%'.format(temperature, pressure, humidity))
    time.sleep(1)
