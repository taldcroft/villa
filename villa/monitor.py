import os
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive plotting

import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from astropy.time import Time
import astropy.units as u
from astropy.table import Table

try:
    from .sensors import get_sensors
except ImportError:
    pass

SENSORS_DIR = os.path.join(os.environ['HOME'], 'static', 'sensors')
RECENT_INTERVAL = 7 * u.day


def plot_recent_temps_humidity(dat, fn_plot=None, last_day=False):
    """
    `data` should be a Table with columns `time`, `temp_adc0`, `temp_280`,
    `humidity_280`.
    """
    YMIN = 40  # degF
    YMAX = 70

    fig = plt.figure(figsize=(7, 5))
    ax2 = fig.add_subplot(1, 1, 1)
    plt.ylim(YMIN, YMAX)

    dates = Time(dat['date']).plot_date
    if last_day:
        ok = (Time.now().plot_date - dates) < 1.0
        dat = dat[ok]
        dates = dates[ok]

    temp_adc0 = dat['temp_adc0']
    temp_280 = dat['temp_280']
    humidity280 = dat['humidity_280']

    ax2.set_ylim(0, 100)
    ax2.plot_date(dates, humidity280, 'r-*', label='Humidity')[0]
    ax2.set_ylabel('Humidity %')
    ax2.set_xlabel('Time (GMT, last data {})'.format(dat['date'][-1]))

    ax = ax2.twinx()
    ax.plot_date(dates, temp_adc0, '.-c', label='Temp ADC')[0]
    ax.plot_date(dates, temp_280, '.-b', label='Temp BME')[0]
    ax.set_ylabel('Temperature (degF)')
    plt.title('Villa temperature (blue, cyan) and humidity (red)')
    plt.grid()
    plt.legend(loc='upper left', fontsize='small')

    if last_day:
        formatter = DateFormatter('%H:%M')
    else:
        formatter = DateFormatter('%Y-%m-%d')
    ax.xaxis.set_major_formatter(formatter)
    fig.autofmt_xdate()

    temp_both = np.concatenate([temp_adc0, temp_280])
    ymin = np.min(temp_both)
    ymax = np.max(temp_both)
    ymin = min(ymin, YMIN)
    ymax = max(ymax, YMAX)
    ax.set_ylim(ymin, ymax)

    plt.legend(loc='lower left', fontsize='small')
    plt.tight_layout()
    plt.draw()
    plt.show()

    if fn_plot:
        plt.savefig(fn_plot)


def update_sensor_tables(fn_all, fn_recent):
    # Get new sensor data point (dict of sensor readings)
    sensors = {key: '{:.1f}'.format(val) for key, val in get_sensors().items()}

    # Add date key
    now = Time.now()
    now.precision = 0
    sensors['date'] = now.isot

    # First all.dat.  Append a new row (or write from scratch)
    names = sorted(sensors)
    if not os.path.exists(fn_all):
        dat = Table(rows=[sensors], names=names)
        dat.write(fn_all, format='ascii')
    else:
        with open(fn_all, 'a') as fh:
            fh.write(' '.join(sensors[key] for key in names) + '\n')

    # Now recent.dat.
    if not os.path.exists(fn_recent):
        dat = Table.read(fn_all, format='ascii', guess=False)
    else:
        dat = Table.read(fn_recent, format='ascii', guess=False)
        dat.add_row(sensors)

    recent = now - RECENT_INTERVAL
    i0 = np.searchsorted(dat['date'], recent.isot)
    dat = dat[i0:]
    dat.write(fn_recent, format='ascii')

    return dat

def main():
    fn_all = os.path.join(SENSORS_DIR, 'all.dat')
    fn_recent = os.path.join(SENSORS_DIR, 'recent.dat')
    fn_plot = os.path.join(SENSORS_DIR, 'recent.png')
    recent = update_sensor_tables(fn_all, fn_recent)

    plot_recent_temps_humidity(recent, fn_plot)

if __name__ == '__main__':
    main()
