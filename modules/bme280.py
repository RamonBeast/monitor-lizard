from smbus import SMBus
from bme280 import BME280
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
        "pressure": sum(p) / len(p),
        "humidity": sum(h) / len(h),
    }

def start(q, cfg):
    # Sensor initialization
    bus = SMBus(1)
    bme280 = BME280(i2c_dev=bus)
    bme280.setup(mode="forced")

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
