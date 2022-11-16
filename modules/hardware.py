from subprocess import PIPE, Popen
from time import sleep

def get_cpu_temperature():
    """ Returns the Raspberry Pi temperature in Celsius degrees
    """

    process = Popen(['vcgencmd', 'measure_temp'], stdout=PIPE)
    output, _error = process.communicate()
    output = str(output.decode())

    return float(output[output.index('=') + 1:output.rindex("'")])

def start(q, cfg):
    while True:
        # Read CPU temp
        cpu_temp = get_cpu_temperature()
        
        p = {
            "measurement": cfg['measurement'],
            "tags": {
                "location": cfg['location'],
                "asset": cfg['asset']
            },
            "fields": {
                "cpu_temp": cpu_temp
            }
        }

        q.put((__name__, cfg['bucket'], p, 's'))
        sleep(cfg['poll-time'])
