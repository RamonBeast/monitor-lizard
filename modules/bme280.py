from smbus import SMBus
from bme280 import BME280
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
        "pressure": sum(p) / len(p),
        "humidity": sum(h) / len(h),
    }

def start(q, cfg):
    # Sensor initialization
    bus = SMBus(1)
    bme280 = BME280(i2c_dev=bus)

    # Discard the first readings as they're usually wrong
    _ = get_smoothed_readings(bme280, samples=2)

    while True:
        # Read sensor
        r = get_smoothed_readings(bme280)
        
        p = {
            "measurement": cfg['measurement'],
            "tags": {
                "location": cfg['location'],
                "asset": cfg['asset']
            },
            "fields": {
                "temperature": r["temperature"],
                "humidity": r["humidity"],
                "pressure": r["pressure"]
            }
        }

        q.put((__name__, cfg['bucket'], p, 's'))
        sleep(cfg['poll-time'])
