import pexpect
import time
import shutil
import os
import requests
import requests.exceptions
from astropy.table import Table
from astropy.time import Time
import astropy.units as u
import numpy as np
from scipy.signal import medfilt

import smtplib
from email.mime.text import MIMEText
import logging

from . import monitor

ROOTDIR = os.path.join(os.environ['HOME'], 'villa')
RECENT = os.path.join(ROOTDIR, 'recent.dat')
fail_log_fn = os.path.join(ROOTDIR, 'fail.log')
timeout = 30
rooturl = 'http://76.179.57.252/static/sensors/'
villa_ip = '76.179.57.252'
recipients = ['taldcroft@gmail.com', 'anetasie@gmail.com',
              '6177214364@vtext.com', '3392937602@msg.fi.google.com']

ALERT_TEMP = 40  # deg F


logging.basicConfig(level=logging.INFO)

def get_recent_data():
    """Get recent temperature data file using scp"""
    logging.debug('Getting recent temperature data file')
    passwd = open(os.path.join(ROOTDIR, 'passwd'), 'r').read()
    cmd = ('scp pi@{}:/home/pi/static/sensors/recent.dat {}'
           .format(villa_ip, RECENT))
    proc = pexpect.spawn(cmd)
    proc.expect('password: ')
    proc.sendline(passwd)
    proc.expect(pexpect.EOF)


def read_recent_data():
    logging.debug('Reading recent temperature data')
    dat = Table.read(RECENT, format='ascii', guess=False)
    return dat


def plot_recent_data(dat):
    logging.debug('Making plot of recent day and week')
    for fn, last_day in (('recent-week.png', False),
                         ('recent-day.png', True)):
        outfile = os.path.join(ROOTDIR, fn)
        monitor.plot_recent_temps_humidity(dat, outfile, last_day=last_day)
        shutil.copy(outfile, '/home/aldcroft/www.new/villa/')


def sendmail(recipients, text, subject):
    me = os.environ['USER'] + '@head.cfa.harvard.edu'
    msg = MIMEText(text)
    msg['Subject'] = subject
    msg['From'] = me
    msg['To'] = ','.join(recipients)
    s = smtplib.SMTP('localhost')
    s.sendmail(me, recipients, msg.as_string())
    s.quit()


def send_email_alert(date):
    logging.warning('Sending alert for low temperature!')
    subject = 'VILLA TEMPERATURE ALERT {}!!'.format(date)
    text = """ALERT:
Villa temperature may be too low at {}.  Check

  http://hea-www.harvard.edu/~aldcroft/villa/
""".format(date)
    sendmail(recipients, text, subject)


def check_recent_data(dat):
    logging.debug('Checking recent data for low temperature')
    date_1day_ago = (Time.now() - 1 * u.day).isot
    ok = dat['date'] > date_1day_ago
    dat = dat[ok]
    vals = np.vstack([dat['temp_280'], dat['temp_adc0']]).transpose().flatten()
    med_vals = medfilt(vals, 11)  # 25 minutes (5x5) of samples between the two sensors

    bad = med_vals < ALERT_TEMP
    if np.any(bad):
        idx_bad = (np.flatnonzero(bad) // 2)[-1]
        date = dat['date'][idx_bad]
    else:
        date = None

    return date


def main():
    get_recent_data()
    dat = read_recent_data()
    plot_recent_data(dat)
    date = check_recent_data(dat)
    if date:
        send_email_alert(date)


def get_file_by_web(name):
    """Doesn't really work since pi web server is not stable"""
    try:
        response = requests.get(rooturl + name, stream=True, timeout=timeout)
    except requests.exceptions.Timeout as err:
        with open(fail_log_fn, 'a') as fh:
            print('{}: {} server timeout {} seconds'
                  .format(name, time.ctime(), timeout),
                  file=fh)
    except Exception as err:
        with open(fail_log_fn, 'a') as fh:
            print('{}: {} {}'.format(name, time.ctime(), err), file=fh)
    else:
        fn = os.path.join(ROOTDIR, name)
        with open(fn, 'wb') as fh:
            shutil.copyfileobj(response.raw, fh)
        del response


if __name__ == '__main__':
    main()
