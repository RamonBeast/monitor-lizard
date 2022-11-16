import RPi.GPIO as GPIO
from collections import deque
from datetime import datetime
from datetime import timedelta
from time import sleep

# This method fires on edge detection
def countme(channel, dq):
    timestamp = datetime.now()
    dq.append(timestamp)

def start(q, cfg):
    counts = deque()

    # Configure board count mode
    GPIO.setmode(GPIO.BOARD)

    # Set the input with falling edge detection for geiger counter pulses
    pin = cfg['pin']
    GPIO.setup(pin, GPIO.IN)
    GPIO.add_event_detect(7, GPIO.FALLING, callback=lambda x: countme(pin, counts))

    # We sleep immediately as we need to acquire 1 minute of data
    sleep(60)

    while True:
        # Remove pulses older than 1 minute
        while len(counts) and counts[0] < datetime.now() - timedelta(seconds=60):
            counts.popleft()

        p = {
            "measurement": cfg['measurement'],
            "tags": {
                "location": cfg['location'],
                "asset": cfg['asset']
            },
            "fields": {
                "cpm": len(counts),
                "usv_h": len(counts) * cfg['usvh-ratio']
            }
        }

        q.put((__name__, cfg['bucket'], p, 's'))

        # Empty the queue
        counts.clear()

        sleep(cfg['poll-time'])