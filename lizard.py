import influxdb_client
import yaml, sys, stat, os
from multiprocessing import Process, Queue
from importlib import import_module

def load_conf(conf='config.yaml'):
    with open(conf) as f:
        cfg = yaml.load(f, Loader=yaml.FullLoader)

    return cfg

def get_clients(db_cfg):
    clients = {}

    url = db_cfg['url']
    org = db_cfg['org']

    for bucket, token in db_cfg['buckets'].items():
        clients[bucket] = influxdb_client.InfluxDBClient(url=url, token=token, org=org)

    return clients

def start_modules(q, cfg):
    jobs = []

    for name, m_cfg in cfg.items():
        if m_cfg['active'] == False:
            print(f'Module {name} is not active, moving on')
            continue

        print(f'Module {name} is being activated')
        
        mod = None

        # Import modules dynamically
        try:
            mod = import_module('modules.' + name)
        except ModuleNotFoundError:
            print(f'Module {name} not found in modules folder')
            continue

        if 'start' not in dir(mod):
            print(f'Module {name} does not contain any start() function')
            continue

        p = Process(target=mod.start, args=(q, m_cfg))
        jobs.append(p)

    for j in jobs:
        j.start()

    return jobs

def main():
    if len(sys.argv) < 2:
        print("Error: No configuration file specified")
        print(f"python {sys.argv[0]} <path to config file>")
        return 1

    q = Queue()
    cfg = load_conf(sys.argv[1])

    # Sanity check on modules folder
    if os.path.isdir('modules') == False:
        print('Cannot locate \"modules\" folder, exiting')
        return 1

    m = os.lstat('modules').st_mode

    if (stat.S_IWOTH & m) and cfg['config']['allow-writeable-modules'] == False:
        print('Warning: \"modules\" folder is world-writeable, anyone could drop-in a script and execute code on this device.')
        print('You should make the folder not world-writeable: \"chmod o-w modules\"')
        print('If this is not possible, you can enable \"allow-writeable-modules\" in the configuration file')
        return 1

    clients = get_clients(cfg['influx'])
    jobs = start_modules(q, cfg['modules'])

    while True:
        name, bucket, record, precision = q.get()

        if bucket not in clients:
            print(f'Bucket {bucket} not found in configuration file for module {name}')
            continue
    
        client = clients[bucket]

        with client.write_api() as write_api:
            write_api.write(bucket, record=record, write_precision=precision)

    # Wait on all processes
    for j in jobs:
        j.join()

    print("All of Lizard's modules have terminated")
    return 0

if __name__ == '__main__':
    exit(main())

