from smbus import SMBus
from bmp280 import BMP280
from time import sleep

# The sensor has a resolution of 1Hz
def get_smoothed_readings(sensor, samples=3):
    # Read sensor
    t = []
    p = []
    h = []

    for _ in range(samples):
        t.append(sensor.get_temperature())
        p.append(sensor.get_pressure())
        h.append(sensor.get_humidity())

        sleep(1)

    return {
        "temperature": sum(t) / len(t),
        "humidity": sum(h) / len(h),
    }

def start(q, cfg):
    # Sensor initialization
    bus = SMBus(1)
    bmp280 = BMP280(i2c_dev=bus)

    # Discard the first readings as they're usually wrong
    _ = get_smoothed_readings(bmp280, samples=2)

    while True:
        # Read sensor
        r = get_smoothed_readings(bmp280)
        
        p = {
            "measurement": cfg['measurement'],
            "tags": {
                "location": cfg['location'],
                "asset": cfg['asset']
            },
            "fields": {
                "temperature": r["temperature"],
                "pressure": r["pressure"]
            }
        }

        q.put((__name__, cfg['bucket'], p, 's'))
        sleep(cfg['poll-time'])
