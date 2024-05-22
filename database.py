import aiosqlite

DATABASE = 'sensor_data.db'

async def init_db():
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS sensor_data (
                id INTEGER PRIMARY KEY,
                sensor1 REAL,
                sensor2 REAL,
                sensor3 REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.commit()

async def insert_sensor_data(sensor1, sensor2, sensor3):
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute('''
            INSERT INTO sensor_data (sensor1, sensor2, sensor3)
            VALUES (?, ?, ?)
        ''', (sensor1, sensor2, sensor3))
        await db.commit()

async def fetch_latest_sensor_data():
    async with aiosqlite.connect(DATABASE) as db:
        async with db.execute('''
            SELECT sensor1, sensor2, sensor3, timestamp
            FROM sensor_data
            ORDER BY timestamp DESC
            LIMIT 1
        ''') as cursor:
            return await cursor.fetchone()