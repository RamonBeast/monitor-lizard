from smbus import SMBus
from bmp280 import BMP280
from time import sleep

def get_smoothed_readings(sensor, samples=3):
    # Read sensor
    t = []
    p = []
    h = []

    for _ in range(samples):
        t.append(sensor.get_temperature())
        p.append(sensor.get_pressure())
        h.append(sensor.get_humidity())

        sleep(0.5)

    return {
        "temperature": sum(t) / len(t),
        "humidity": sum(h) / len(h),
    }

def start(q, cfg):
    # Sensor initialization
    bus = SMBus(1)
    bmp280 = BMP280(i2c_dev=bus)
    bmp280.setup(mode="forced")

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
