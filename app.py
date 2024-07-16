from flask import Flask, render_template, jsonify, request
from database import init_db, fetch_average_sensor_data_per_day, fetch_average_sensor_data_per_hour, fetch_actions_and_prepare
from util import Util, UIConfigs
from datetime import datetime, timedelta, date
from automation import Automation
from hardware import Hardware

app = Flask(__name__)
config = UIConfigs()
hardware = Hardware()
automation = Automation()

with app.app_context():
    init_db()
    automation.start()

@app.route('/')
def index():
    data = {}
    dt_from = datetime.now() - timedelta(days=15)
    dt_to = datetime.now()
    dt_from = dt_from.replace(hour=0, minute=0, second=0, microsecond=0)
    dt_to = dt_to.replace(hour=0, minute=0, second=0, microsecond=0)
    data['sensors'] = fetch_average_sensor_data_per_day(dt_from, dt_to)
    data['actions'] = Util.fetch_and_separete_actions(dt_from, dt_to)
    today = date.today()
    return render_template('index.html', pins=Util.get_pins(), data=data, today=today)

@app.route('/settings', methods=['GET'])
def settings_get():
    return jsonify(config.read_all())

@app.route('/settings', methods=['POST'])
def settings_post():
    data = request.get_json()
    for value_pair in data:
        name = value_pair['name']
        value = value_pair['value']
        if 'name' not in value_pair or 'value' not in value_pair:
            return 'Bad request, "name" and "value" attributes required', 400
    for value_pair in data:
        name = value_pair['name']
        value = value_pair['value']
        config.write(name, value)
    hardware.init_gpio()
    automation.restart()
    return 'OK', 200

@app.route('/sensor_values', methods=['GET'])
def sensor_values():
    return jsonify(
        temperature=round(hardware.temperature, 1),
        humidity=round(hardware.humidity, 1),
        soil_moisture=round(hardware.soil_moisture, 1),
        light=hardware.light.value,
        fan=hardware.fan.value,
        wind=hardware.wind.value,
        pump=hardware.pump.value
    )

@app.route('/chart_data', methods=['GET'])
def chart_data():
    dt_from = datetime.strptime(request.args.get('from'), '%Y-%m-%d')
    dt_to = datetime.strptime(request.args.get('to'), '%Y-%m-%d')
    data = {}
    if dt_to - dt_from == timedelta(days=1):
        data['sensors'] = fetch_average_sensor_data_per_hour(dt_from, dt_to)
    else:
        data['sensors'] = fetch_average_sensor_data_per_day(dt_from, dt_to)
    data['actions'] = fetch_actions_and_prepare(dt_from, dt_to)
    import pprint
    pprint.pprint(data['actions'])
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True, host='worg.local', use_reloader=False)