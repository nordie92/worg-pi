import sqlite3
from datetime import datetime, timedelta
import random
import argparse

DATABASE = 'sqlite.db'

def init_db():
    with sqlite3.connect(DATABASE) as db:
        db.execute('''
            CREATE TABLE IF NOT EXISTS sensors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                time TIMESTAMP NOT NULL,
                temperature REAL NOT NULL,
                humidity REAL NOT NULL,
                soil_humidity REAL NOT NULL
            )
        ''')
        db.execute('''
            CREATE TABLE IF NOT EXISTS actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                time TIMESTAMP NOT NULL,
                actor TEXT NOT NULL,
                state TEXT NOT NULL
            )
        ''')
        db.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                comment TEXT NOT NULL
            )
        ''')
        db.commit()

def insert_sensor_data(temperature, humidity, soil_humidity):
    with sqlite3.connect(DATABASE) as db:
        db.execute('''
            INSERT INTO sensors (time, temperature, humidity, soil_humidity)
            VALUES (?, ?, ?, ?)
        ''', (datetime.now(), temperature, humidity, soil_humidity))
        db.commit()

def fetch_latest_sensor_data():
    with sqlite3.connect(DATABASE) as db:
        cursor = db.execute('SELECT * FROM sensors ORDER BY time DESC LIMIT 1')
        row = cursor.fetchone()
        return row

def fetch_first_sensor_data():
    with sqlite3.connect(DATABASE) as db:
        cursor = db.execute('SELECT * FROM sensors ORDER BY time ASC LIMIT 1')
        row = cursor.fetchone()
        return row

def fetch_sensor_data(dt_from, dt_to):
    with sqlite3.connect(DATABASE) as db:
        cursor = db.execute('''
            SELECT * FROM sensors
            WHERE time BETWEEN ? AND ?
            ORDER BY time
        ''', (dt_from, dt_to))
        rows = cursor.fetchall()
        return rows

def fetch_average_sensor_data_per_day(dt_from, dt_to):
    with sqlite3.connect(DATABASE) as db:
        cursor = db.execute('''
            SELECT strftime('%Y-%m-%dT00:00:00', time) as time, AVG(temperature) as temperature, AVG(humidity) as humidity, AVG(soil_humidity) as soil_humidity
            FROM sensors
            WHERE time BETWEEN ? AND ?
            GROUP BY strftime('%Y%m%d', time)
            ORDER BY strftime('%Y%m%d', time)
        ''', (dt_from, dt_to))
        rows = cursor.fetchall()
        return rows

def fetch_average_sensor_data_per_hour(dt_from, dt_to):
    with sqlite3.connect(DATABASE) as db:
        cursor = db.execute('''
            SELECT strftime('%Y-%m-%dT%H:00:00', time) as time, AVG(temperature) as temperature, AVG(humidity) as humidity, AVG(soil_humidity) as soil_humidity
            FROM sensors
            WHERE time BETWEEN ? AND ?
            GROUP BY strftime('%Y%m%d%H', time)
            ORDER BY strftime('%Y%m%d%H', time)
        ''', (dt_from, dt_to))
        rows = cursor.fetchall()
        return rows

def fetch_actions(dt_from, dt_to):
    with sqlite3.connect(DATABASE) as db:
        cursor = db.execute('''
            SELECT id, strftime('%Y-%m-%dT%H:%M:%S', time) as time, actor, state FROM actions
            WHERE time BETWEEN ? AND ?
            ORDER BY time
        ''', (dt_from, dt_to))
        rows = cursor.fetchall()
        return rows

def clear_db():
    with sqlite3.connect(DATABASE) as db:
        db.execute('DELETE FROM sensors')
        db.execute('DELETE FROM actions')
        db.execute('DELETE FROM comments')
        db.commit()

def generate_example_data(dt_from, dt_to):
    generate_example_data_sensors(dt_from, dt_to)
    generate_example_data_actions(dt_from, dt_to)
    generate_example_data_comments(dt_from, dt_to)

def generate_example_data_sensors(dt_from, dt_to):
    with sqlite3.connect(DATABASE) as db:
        current = dt_from
        while current <= dt_to:
            db.execute('''
                INSERT INTO sensors (time, temperature, humidity, soil_humidity)
                VALUES (?, ?, ?, ?)
            ''', (
                current,
                random.uniform(10, 30),
                random.uniform(30, 90),
                random.uniform(10, 50)
            ))
            current += timedelta(seconds=60)
        db.commit()

def generate_example_data_actions(dt_from, dt_to):
    with sqlite3.connect(DATABASE) as db:
        current = dt_from
        while current <= dt_to:
            # Light on at 06:00
            light_on_time = datetime.combine(current.date(), datetime.min.time()) + timedelta(hours=6)
            db.execute('''
                INSERT INTO actions (time, actor, state)
                VALUES (?, ?, ?)
            ''', (light_on_time, 'light', 'on'))

            # Light off at 22:00
            light_off_time = datetime.combine(current.date(), datetime.min.time()) + timedelta(hours=22)
            db.execute('''
                INSERT INTO actions (time, actor, state)
                VALUES (?, ?, ?)
            ''', (light_off_time, 'light', 'off'))

            # Pump on/off every 4 hours
            pump_time = datetime.combine(current.date(), datetime.min.time())
            for i in range(0, 24, 4):
                pump_on_time = pump_time + timedelta(hours=i)
                pump_off_time = pump_on_time + timedelta(seconds=5)
                db.execute('''
                    INSERT INTO actions (time, actor, state)
                    VALUES (?, ?, ?)
                ''', (pump_on_time, 'pump', 'on'))
                db.execute('''
                    INSERT INTO actions (time, actor, state)
                    VALUES (?, ?, ?)
                ''', (pump_off_time, 'pump', 'off'))
            
            current += timedelta(days=1)
        db.commit()

def generate_example_data_comments(dt_from, dt_to):
    with sqlite3.connect(DATABASE) as db:
        current = dt_from
        while current <= dt_to:
            db.execute('''
                INSERT INTO comments (date, comment)
                VALUES (?, ?)
            ''', (
                current.date(),
                f"Example comment for {current.date()}"
            ))
            current += timedelta(days=1)
        db.commit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Rufe Funktionen aus einem Python-Skript auf.')
    parser.add_argument('funktion', choices=['clear', 'init', 'generate'], help='Die Funktion, die aufgerufen werden soll')

    args = parser.parse_args()

    if args.funktion == 'clear':
        print('clear db...')
        clear_db()
        print('db cleard')
    elif args.funktion == 'init':
        print('init db...')
        init_db()
        print('db inited')
    elif args.funktion == 'generate':
        print('generate example data for last 182 days...')
        generate_example_data(datetime.now() - timedelta(days=182), datetime.now() + timedelta(days=1))
        print('example data generated')