from time import sleep
import requests

def get_outdoor_data(lat, lon, api_key):
    r = requests.get(f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}')

    if r.status_code != 200:
        return {}

    data = r.json()

    return {
        "temperature": data["main"]["temp"] - 273.15,
        "humidity": float(data["main"]["humidity"]),
    }
    
def start(q, cfg):
    while True:
        # Get outdoor data from the API
        r = get_outdoor_data(cfg['lat'], cfg['lon'], cfg['ow-key'])
        
        if len(r) == 0:
            print('Cannot read data from weather API')
            return 1

        p = {
            "measurement": cfg['measurement'],
            "tags": {
                "location": "outdoor"
            },
            "fields": {
                "temperature": r["temperature"],
                "humidity": r["humidity"]
            }
        }

        q.put((__name__, cfg['bucket'], p, 's'))
        sleep(cfg['poll-time'])
