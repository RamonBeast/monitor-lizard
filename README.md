# Monitor Lizard
**Monitor Lizard** is a project that gathers data from a variety of sensors. It is intended to be easy to use and flexible to expand. Although this project uses a `Raspberry Pi`, this is not a requirement. Sensor data is written to an [InfluxDB](https://docs.influxdata.com/influxdb/v2.5/install/) instance where it can be visualized using [Grafana](https://grafana.com/grafana/download).

Currently supported modules are:

- `BME280` that reads data from a [BME280](https://github.com/pimoroni/bme280-python): temperature, humidity and barometric pressure
- `BMP280` reads data from a [BMP280](https://github.com/pimoroni/bmp280-python): temperature and barometric pressure
- `Outdoor` that uses [OpenWeather API](https://openweathermap.org/api) (free) to acquire outdoor information: temperature and humidity
- `Hardware` that logs the temperature of the `Raspberry Pi` CPU
- `Geiger` that uses the [Geiger RadiationD board](https://github.com/RamonBeast/Geiger-Counter-RadiationD-v1.1-CAJOE) to calculate the level of background radiation

All modules can be enabled and disabled as desired from the `config.yaml` file.

## Pre-requisites
- InfluxDB instance
- Grafana

## InfluxDB
After installing [InfluxDB](https://docs.influxdata.com/influxdb/v2.5/install/) it is suggested to create 2 different buckets, one for  environmental monitoring and one for hardware information coming from the `Raspberry Pi`. Both the `buckets` and their respective access `tokens` can be generated directly from the `InfluxDB` dashboard, locally available usually at: `http://localhost:8086`

## Grafana
After installing [Grafana](https://grafana.com/grafana/download) it is possible to bootstrap an initial dashboard by importing the [grafana.json](assets/grafana.json) file. This configuration uses 2 buckets: `lizard` for environmental data and `hardware` for hardware data. The `Flux` queries should be adjusted to reflect the names of your assets, but each widget can easily be edited directly within the `Grafana` UI.

## Raspberry Pi
In order to use the `I2C` based sensors, `I2C` must be enabled on the board. This is easily achieved by running `sudo raspi-config` -> `Interface Options` -> `I2C` and enabling the option. Do not forget to reboot the board afterwards: `sudo reboot`.

### Geiger module
The Geiger module requires +5V, a GND connection and a connection to any `GPIO` pin (on the Geiger board the sensor **output** is marked as `VIN`, be careful not to erroneously provide voltage on this pin). By default the pin used is the number `7` on the Raspberry board, this setting can be changed in the configuration file by altering the `pin` parameter. The default multiplication factor to calculate `uSieverts` from `CPM` is related to the `J305` tube that comes by default with this board, it can be adjusted in the `config.yaml` to match any other tube simply by changing the `usvh-ratio` parameter.

![Geiger board](assets/geiger.jpg?raw=true "Geiger Board")

These are the `J305` specs:

![J305 specs](assets/j305_specs.jpg?raw=true "J305 specs")

More details on this board can be found [here](https://github.com/RamonBeast/Geiger-Counter-RadiationD-v1.1-CAJOE).

### BME280
This is a pressure, temperature and humidity sensor:

![BME280](assets/bme280.jpg?raw=true "BME280")

The sensor requires 4 connections:

- 3.3V (PIN17)
- GND (PIN14)
- SDA (PIN3)
- SDL (PIN5), `SDL` is referred to as `SCL` on the sensor shown in the picture above

![Raspberry Pi 4 pinout](assets/pinout.png?raw=true "Raspberry Pi 4 pinout")

After connecting it to the board, turn it on and issue the following commands:

```
$ sudo apt-get install i2c-tools
$ i2cdetect -y 1

     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:                         -- -- -- -- -- -- -- --
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
70: -- -- -- -- -- -- 76 --
```

The sensor should appear at the adderss `0x76`, some batches though are set at the address `0x77`, if nothing shows up, check the wiring. The sensor does not provide accurate reading on first access, so it's suggested to discard the first reading. `monitor-lizard` takes care of this aspect automatically.

### BMP280
This is a lower cost alternative to the `BME280` that provides pressure and temperature readings (humidity sensor is not present). The `BMP280` uses the same address as the `BME280` but having both on the same board is redundant, so this shouldn't be an issue. However if both are required to operate on the same board, and if there is a conflict with I2C addresses, additional I2C ports can be created by converting GPIO pins as described in [this article](https://medium.com/cemac/creating-multiple-i2c-ports-on-a-raspberry-pi-e31ce72a3eb2).

## Configuration
Copy `cfg/config-sample.yaml` to `cfg/config.yaml` and add your own settings (api keys and tokens) as desired. A minimal configuration would look like this:

```
influx:
  url: http://localhost:8086
  org: home
  buckets:
    lizard: AAAAAAA==
    hardware: BBBBBB==

modules:
  geiger:
    active: true
    bucket: lizard
    usvh-ratio: 0.00812037037037 # This value is for Geiger tube model J305
    pin: 7 # board pin where the pulse out is connected
    location: indoor
    poll-time: 60 # poll sensor every x seconds (default: 1 minute)
    measurement: environment # measurement
    asset: geiger_board

hardware:
    active: true
    bucket: hardware
    poll-time: 900 # poll sensor every x seconds (default: 15 minutes)
    measurement: hardware # measurement
    asset: pihole
    location: indoor
```

## Installation
- Clone this repo: `git clone git@github.com:RamonBeast/monitor-lizard.git`
- Move into the project directory: `cd monitor-lizard`
- Create a virtual environment: `virtualenv .venv` then activate it `. .venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`
- Copy `cfg/config-sample.yaml` to `cfg/config.yaml` and adjust the configuration according to your preference

## Running Manually
After the installation `monitor-lizard` can be started manually, if a service is not required:

```
cd /path/to/monitor-lizard/
. .venv/bin/activate
python lizard.py cfg/config.yaml
```

## Daemon (systemd) configuration
Update `utils/monitor-lizard.service` to reflect your `monitor-lizard` project's path, then run the following commands to activate a service that starts automatically at boot:

```
cd /path/to/monitor-lizard
sudo cp utils/monitor-lizard.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable monitor-lizard.service
sudo systemctl start monitor-lizard.service
```

Service status can be checked with:
```
$ systemctl status monitor-lizard.service

● monitor-lizard.service - Monitor-Lizard service
     Loaded: loaded (/etc/systemd/system/monitor-lizard.service; enabled; vendor preset: enabled)
     Active: active (running) since Tue 2022-11-15 19:10:20 CET; 3h ago
   Main PID: 753 (python)
      Tasks: 10 (limit: 4164)
        CPU: 20.119s
     CGroup: /system.slice/monitor-lizard.service
             ├─753 /home/<user>/monitor-lizard/.venv/bin/python /home/<user>/monitor-lizard/lizard.py /home/<user>/monitor-lizard/cfg/config.yaml
             ├─757 /home/<user>/monitor-lizard/.venv/bin/python /home/<user>/monitor-lizard/lizard.py /home/<user>/monitor-lizard/cfg/config.yaml
             ├─758 /home/<user>/monitor-lizard/.venv/bin/python /home/<user>/monitor-lizard/lizard.py /home/<user>/monitor-lizard/cfg/config.yaml
             ├─759 /home/<user>/monitor-lizard/.venv/bin/python /home/<user>/monitor-lizard/lizard.py /home/<user>/monitor-lizard/cfg/config.yaml
             └─760 /home/<user>/monitor-lizard/.venv/bin/python /home/<user>/monitor-lizard/lizard.py /home/<user>/monitor-lizard/cfg/config.yaml
```

Logs can be obtained by running:
```
$ journalctl -u monitor-lizard.service

Nov 15 19:10:20 <host> systemd[1]: Started Monitor-Lizard service.
Nov 15 19:10:23 <host> python[753]: Module bme280 is being activated
Nov 15 19:10:23 <host> python[753]: Module outdoor is being activated
Nov 15 19:10:23 <host> python[753]: Module geiger is being activated
```

# Writing additional modules
Adding new modules to `monitor-lizard` can be done in 3 steps:

1. Create the sensor script in the `module` folder
1. Add a related configuration section in the `config.json` file

## Module structure
Each module requires a `start()` function that takes 2 parameters: 

1. a `q` parameter representing a `Queue` created by `lizard.py` and used by the script to send sensor data
1. a `cfg` parameter containing module-specific parameters from the `config.json` file

A minimal `start()` function contains sensor reading and data sending functions in an infinite loop.

```
def start(q, cfg):
    while True:
        # Read sensor (this is the function you will want to populate)
        data = get_data_from_sensor()
        
        p = {
            "measurement": cfg['measurement'],
            "tags": {
                "location": cfg['location'],
                "asset": cfg['asset']
            },
            "fields": {
                ... your fields and data
            }
        }

        q.put((__name__, cfg['bucket'], p, 's'))
        sleep(cfg['poll-time'])
```

## Configuration structure
A module configuration requires the following mandatory parameters:

```
my_new_module:
    active: true or false
    bucket: bucket_name
    poll-time: 900 (in seconds)
    measurement: measurement_name
    location: asset_location
```

Any other parameter is module-specific and it will automatically be passed to the `start()` method after loading the configuration file.
