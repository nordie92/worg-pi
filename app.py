from flask import Flask, render_template, jsonify
from database import init_db, fetch_latest_sensor_data
from sensor_task import start_task

app = Flask(__name__)

with app.app_context():
    init_db()
    start_task()

@app.route('/')
async def index():
    sensor_data = await fetch_latest_sensor_data()
    if sensor_data:
        sensor_values = sensor_data[:3]
        plot_path = create_plot(sensor_values)
        actuators = control_actuators(sensor_values)
    else:
        sensor_values = []
        plot_path = ""
        actuators = []
    return render_template('index.html', sensor_values=sensor_values, plot_path=plot_path, actuators=actuators)

if __name__ == '__main__':
    app.run(debug=True)