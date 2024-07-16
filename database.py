import sqlite3
from datetime import datetime, timedelta, time
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
                state INTEGER NOT NULL
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

def insert_action(actor, state, time=datetime.now()):
    with sqlite3.connect(DATABASE) as db:
        db.execute('''
            INSERT INTO actions (time, actor, state)
            VALUES (?, ?, ?)
        ''', (time, actor, state))
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
    dt_to = dt_to + timedelta(days=1)
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
    dt_from = dt_from + timedelta(days=1)
    dt_to = dt_to + timedelta(days=1)
    print(dt_from, dt_to)
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

def fetch_actions_and_prepare(dt_from, dt_to):
    dt_from = dt_from + timedelta(days=1)
    dt_to = dt_to + timedelta(days=1)
    with sqlite3.connect(DATABASE) as db:
        cursor = db.execute('SELECT DISTINCT actor FROM actions')
        actors = [row[0] for row in cursor.fetchall()]

        actors_spans = {}

        for actor in actors:
            actors_spans[actor] = []
            cursor = db.execute('''
                SELECT strftime('%Y-%m-%dT%H:%M:%S', time) as time, state FROM actions
                WHERE actor = ? and time BETWEEN ? AND ?
                ORDER BY time
            ''', (actor, dt_from, dt_to))
            rows = cursor.fetchall()
            if len(rows) == 0:
                continue

            spans = []
            last_state = 0
            for action in rows:
                time = action[0]
                state = action[1]

                if last_state == 0 and state == 1:
                    spans.append({'dt_from': time})
                    last_state = 1
                elif last_state == 1 and state == 0:
                    spans[-1]['dt_to'] = time
                    last_state = 0

            if rows[0][1] == 0:
                cursor = db.execute('''
                    SELECT strftime('%Y-%m-%dT%H:%M:%S', time) as time, state FROM actions
                    WHERE actor = ? and time < ? and state = 1
                    ORDER BY time DESC
                ''', (actor, dt_from))
                row = cursor.fetchone()
                spans.insert(0, {'dt_from': row[0], 'dt_to': rows[0][0]})
            
            if rows[-1][1] == 1:
                spans[-1]['dt_to'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
            actors_spans[actor] = spans
        return actors_spans


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
            ''', (light_on_time, 'light', True))

            # Light off at 22:00
            light_off_time = datetime.combine(current.date(), datetime.min.time()) + timedelta(hours=22)
            db.execute('''
                INSERT INTO actions (time, actor, state)
                VALUES (?, ?, ?)
            ''', (light_off_time, 'light', False))

            # Pump on/off every 4 hours
            pump_time = datetime.combine(current.date(), datetime.min.time())
            for i in range(0, 24, 4):
                pump_on_time = pump_time + timedelta(hours=i)
                pump_off_time = pump_on_time + timedelta(seconds=5)
                db.execute('''
                    INSERT INTO actions (time, actor, state)
                    VALUES (?, ?, ?)
                ''', (pump_on_time, 'pump', True))
                db.execute('''
                    INSERT INTO actions (time, actor, state)
                    VALUES (?, ?, ?)
                ''', (pump_off_time, 'pump', False))
            
            # Fan on every 1-3 hours for 30 - 120 minutes
            fan_time = datetime.combine(current.date(), datetime.min.time())
            for i in range(8, 18, random.randint(2, 3)):
                fan_on_time = fan_time + timedelta(hours=i)
                fan_off_time = fan_on_time + timedelta(minutes=random.randint(30, 110))
                db.execute('''
                    INSERT INTO actions (time, actor, state)
                    VALUES (?, ?, ?)
                ''', (fan_on_time, 'fan', True))
                db.execute('''
                    INSERT INTO actions (time, actor, state)
                    VALUES (?, ?, ?)
                ''', (fan_off_time, 'fan', False))
            
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
    parser.add_argument('funktion', choices=['clear', 'init', 'generate', 'actions', 'prepared_actions'], help='Die Funktion, die aufgerufen werden soll')

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
        generate_example_data(datetime.now() - timedelta(days=182), datetime.now() - timedelta(days=1))
        print('example data generated')
    elif args.funktion == 'actions':
        import pprint
        pprint.pprint(fetch_actions(datetime(2000, 1, 1), datetime(2030, 1, 1)))
    elif args.funktion == 'prepared_actions':
        from util import Util
        import pprint
        now = datetime.now()
        # today = datetime.combine(now.date(), time.min)
        today = now
        today = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        print(f'From {today} to {tomorrow}')
        pprint.pprint(Util.fetch_and_separete_actions(today, tomorrow))
        pprint.pprint(fetch_actions_and_prepare(today, tomorrow))