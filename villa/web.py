from flask import Flask, render_template
import villa_mon
import datetime
app = Flask(__name__)

@app.route("/")
def hello():
   now = datetime.datetime.now()
   time_string = now.strftime("%Y-%m-%d %H:%M")

   status = dict(time=time_string,
                 title='HELLO!')
   env_status = {key: '{:.1f}'.format(val) for key, val in villa_mon.get_status().items()}
   
   status.update(env_status)

   return render_template('main.html', **status)

if __name__ == "__main__":
   app.run(host='0.0.0.0', port=80, debug=True)
