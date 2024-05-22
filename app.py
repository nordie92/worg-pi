from flask import Flask, render_template, jsonify
from database import init_db, fetch_average_sensor_data_per_day, fetch_actions
from sensor_task import SensorTask
from util import Util
from datetime import datetime, timedelta

app = Flask(__name__)
sensorTask = SensorTask()

with app.app_context():
    init_db()
    # sensorTask.start_task()

def fetch_and_separete_actions(dt_from, dt_to):
    actions = fetch_actions(dt_from, dt_to)
    actors = {}
    for action in actions:
        time = action[1]
        actor = action[2]
        state = action[3]
        if actor not in actors:
            actors[actor] = []
            if state == 'off':
                actors[actor].append({'dt_from': datetime.strftime(dt_from, '%Y-%m-%dT%H:%M:%S'), 'dt_to': time})
            else:
                actors[actor].append({'dt_from': time, 'dt_to': None})
        else:
            if state == 'on':
                actors[actor].append({'dt_from': time, 'dt_to': None})
            else:
                actors[actor][-1]['dt_to'] = time
    
    # check if some actor is still on
    for actor in actors:
        if actors[actor][-1]['dt_to'] is None:
            actors[actor][-1]['dt_to'] = datetime.strftime(dt_to, '%Y-%m-%dT%H:%M:%S')
    return actors

@app.route('/')
def index():
    data = {}
    dt_from = datetime.now() - timedelta(days=15)
    dt_to = datetime.now()
    dt_from = dt_from.replace(hour=0, minute=0, second=0, microsecond=0)
    dt_to = dt_to.replace(hour=0, minute=0, second=0, microsecond=0)
    data['sensors'] = fetch_average_sensor_data_per_day(dt_from, dt_to)
    data['actions'] = fetch_and_separete_actions(dt_from, dt_to)
    return render_template('index.html', pins=Util.get_pins(), data=data)

if __name__ == '__main__':
    app.run(debug=True, host='worg-pi.local')