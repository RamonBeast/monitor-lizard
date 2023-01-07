# Temporary fix for and open - and ignored - bug in InfluxDB
# https://github.com/influxdata/influxdb/issues/23992
import requests, sys, logging
from datetime import timedelta, datetime

LOG='/path/to/your/log/file'
URL='http://influx_host:8086'
AUTH_TOKEN='Token YOUR-BUCKET-TOKEN'
ORG='YOUR-ORG'
BUCKETS=[
    'bucket-name-a',
    'bucket-name-b'
]

def fix_data(days):
    for b in BUCKETS:
        for d in range(1, days + 1):
            delta = timedelta(days=d)
            t0 = (datetime.now() - delta).replace(hour=0, minute=59, second=59, microsecond=0)
            t1 = (datetime.now() - delta).replace(hour=1, minute=0, second=1, microsecond=0)

            params = { 
                "org": ORG,
                "bucket": b
            }

            body = {
                "start": t0.astimezone().isoformat(),
                "stop": t1.astimezone().isoformat()
            }

            r = requests.post(URL + '/api/v2/delete', json = body , params = params, headers={ "Authorization": AUTH_TOKEN })

            if r.status_code != 200 and r.status_code != 204:
                logging.error(f'Status code error {r.status_code} for request {body} on bucket {b}')
                continue

def main():
    if len(sys.argv) < 2:
        print(f'Usage: python3 {sys.argv[0]} <days>')
        print('\t <days>: number of days to fix, e.g.: 7')
        return 1

    days = sys.argv[1]

    if days.isdigit() == False:
        print(f'days parameter must be a positive number, found: {sys.argv[1]}')
        return 1

    days = int(days)

    logging.basicConfig(
    filename=LOG, 
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    logging.info('Fixing Influx datapoints')
    return fix_data(days)

if __name__ == "__main__":
    sys.exit(main())