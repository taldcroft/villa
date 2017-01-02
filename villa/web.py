import os
from flask import Flask, render_template, send_from_directory
from .sensors import get_sensors
import datetime

app = Flask(__name__, static_folder='/home/pi/static')

@app.route("/")
def hello():
   now = datetime.datetime.now()
   time_string = now.strftime("%Y-%m-%d %H:%M")

   status = dict(time=time_string,
                 title='HELLO!')
   sensors = {key: '{:.1f}'.format(val) for key, val in get_sensors().items()}
   
   status.update(sensors)

   return render_template('main.html', **status)

@app.route('/stat/<path:filename>')
def send_static(filename):
   print('filename={}'.format(filename))
   print('static_folder={}'.format(app.static_folder))
   try:
      out = send_from_directory('/home/pi', 'recent.jpg')
   except Exception as err:
      raise Exception(err)


def main():
   app.run(host='0.0.0.0', port=80, debug=True)

if __name__ == "__main__":
   main()
