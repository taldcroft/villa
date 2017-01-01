from flask import Flask, render_template
from .sensors import get_sensors
import datetime
app = Flask(__name__)

@app.route("/")
def hello():
   now = datetime.datetime.now()
   time_string = now.strftime("%Y-%m-%d %H:%M")

   status = dict(time=time_string,
                 title='HELLO!')
   sensors = {key: '{:.1f}'.format(val) for key, val in get_sensors().items()}
   
   status.update(sensors)

   return render_template('main.html', **status)

def main():
   app.run(host='0.0.0.0', port=80, debug=True)

if __name__ == "__main__":
   main()
